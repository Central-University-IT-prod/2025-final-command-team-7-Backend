import json
import re
from dataclasses import dataclass, field

from openai import AsyncClient

from backend.config.settings import Settings


@dataclass
class MediaSuggestion:
    media_name: str
    confidence: float = field(default=0.5)

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class ChatGPTMediaResult:
    suggestions: list[MediaSuggestion] = field(default_factory=list)
    not_found: bool = False


class GPTService:
    def __init__(self, api_key: str = Settings().GPT_API_KEY, base_url: str = Settings().GPT_BASE):
        self.client = AsyncClient(api_key=api_key, base_url=f"{base_url}/v1")

    def _find_json_objects(self, text: str) -> list[str]:
        objects = []
        brace_level = 0
        start_index = None

        for i, ch in enumerate(text):
            if ch == "{":
                if brace_level == 0:
                    start_index = i
                brace_level += 1
            elif ch == "}":
                brace_level -= 1
                if brace_level == 0 and start_index is not None:
                    obj_str = text[start_index : i + 1]
                    objects.append(obj_str)
                    start_index = None

        return objects

    def _extract_json_to_dict(self, text: str) -> dict | None:
        print("Полный текст ответа от GPT:\n", text)

        json_pattern_code_block = r"```(?:json)?\s*([\s\S]*?)\s*```"
        code_blocks = re.findall(json_pattern_code_block, text)
        print(f"Найдено {len(code_blocks)} блок(ов) в тройных бэктиках")

        best_json = None

        def try_parse(raw: str) -> dict | None:
            print(f"Пробуем распарсить фрагмент (первые 200 символов): {raw[:200]!r}")
            try:
                parsed = json.loads(raw)
                print(f"JSON без исправлений успешно распарсился: {parsed}")
                return parsed
            except json.JSONDecodeError as e:
                print(f"Сырая строка не распарсилась: {e}; пробуем фиксить...")
                fixed = self._fix_common_json_errors(raw)
                try:
                    parsed_fixed = json.loads(fixed)
                    print(f"После исправлений JSON распарсился: {parsed_fixed}")
                    return parsed_fixed
                except json.JSONDecodeError as e2:
                    print(f"Не удалось распарсить даже после фиксов: {e2}")
                    return None

        for block in code_blocks:
            data = try_parse(block)
            if data is not None:
                if isinstance(data, dict) and "suggestions" in data:
                    print("В этом блоке есть нужное поле 'suggestions'; возвращаем сразу.")
                    return data
                print("Сохраняем как лучший JSON из бэктиков (без 'suggestions'), но продолжаем поиск.")
                best_json = data

        all_objects = self._find_json_objects(text)
        print(f"Найдено {len(all_objects)} полных JSON-объект(ов) через баланс скобок (fallback)")

        for obj_str in all_objects:
            data = try_parse(obj_str)
            if data is not None:
                if isinstance(data, dict) and "suggestions" in data:
                    print("Найден JSON с 'suggestions' в fallback, возвращаем сразу.")
                    return data
                print("JSON в fallback корректен, но без 'suggestions'. Запоминаем.")
                best_json = data

        print(f"Возвращаем best_json: {best_json}")
        return best_json

    def _fix_common_json_errors(self, json_str: str) -> str:
        fixed = re.sub(r"\bTrue\b", "true", json_str)
        fixed = re.sub(r"\bFalse\b", "false", fixed)
        fixed = re.sub(r"\bNone\b", "null", fixed)

        if "'" in fixed and '"' not in fixed:
            fixed = fixed.replace("'", '"')

        fixed = re.sub(r",\s*}", "}", fixed)
        fixed = re.sub(r",\s*\]", "]", fixed)

        fixed = re.sub(r"//.*?$", "", fixed, flags=re.MULTILINE)
        fixed = re.sub(r"/\*.*?\*/", "", fixed, flags=re.DOTALL)

        def fix_inner_quotes(m: re.Match) -> str:
            text = m.group(0)
            inner = text[1:-1]
            inner_escaped = re.sub(r'(?<!\\)"', r"\"", inner)
            return f'"{inner_escaped}"'

        fixed = re.sub(r'"([^"\\]*(\\.[^"\\]*)*)"', fix_inner_quotes, fixed)

        return fixed

    async def identify_multiple_media(self, description: str, limit: int = 10) -> ChatGPTMediaResult:
        prompt = (
            f"На основе данного описания: '{description}', определи до {limit} различных медиа произведений, "
            "которые могут соответствовать этому описанию.\n\n"
            "Рассмотри все типы медиа контента:\n"
            "- Фильмы\n"
            "- ТВ сериалы\n"
            "- Аниме и мультфильмы\n"
            "- Документальные фильмы и сериалы\n\n"
            "Вывод должен быть <important>на русском языке и строго в следующем формате JSON</important>:\n"
            "```json\n"
            "{\n"
            '  "suggestions": [\n'
            '    {"media_name": "Оригинальное название произведения 1 для поиска в IMDB на русском", "confidence": 0.9},\n'
            '    {"media_name": "Оригинальное название произведения 2 для поиска в IMDB на русском", "confidence": 0.7}\n'
            "  ],\n"
            '  "not_found": false\n'
            "}\n"
            "```\n\n"
            "Если не удаётся определить, верни:\n"
            "```json\n"
            '{"suggestions": [], "not_found": true}\n'
            "```\n\n"
            "В ОТВЕТЕ ВСЕГДА <important>ТОЛЬКО JSON</important>."
        )

        try:
            response = await self.client.chat.completions.create(
                model="claude-3-sonnet-20240229", messages=[{"role": "user", "content": prompt}], temperature=1
            )
            response_text = response.choices[0].message.content
            print(response_text)
            json_data = self._extract_json_to_dict(response_text)
            print(json_data)

            if not json_data or not isinstance(json_data.get("suggestions"), list):
                return ChatGPTMediaResult(not_found=True)

            suggestions = []
            for suggestion in json_data.get("suggestions", []):
                if isinstance(suggestion, dict) and "media_name" in suggestion:
                    confidence = suggestion.get("confidence", 0.5)
                    if not isinstance(confidence, (int, float)):
                        confidence = float(confidence) if str(confidence).replace(".", "").isdigit() else 0.5
                    suggestions.append(MediaSuggestion(media_name=suggestion["media_name"], confidence=confidence))

            return ChatGPTMediaResult(
                suggestions=suggestions, not_found=json_data.get("not_found", len(suggestions) == 0)
            )
        except Exception as e:
            print(f"GPT Error: {e!s}")
            return ChatGPTMediaResult(not_found=True)

    async def generate_gradient_colors(self, title: str) -> tuple[str, str]:
        prompt = (
            f"Предложи два цвета градиента (в формате HEX, например #FF5733) для темы '{title}', "
            "которые символически подходят к этой теме. Цвета должны быть не пёстрые и не тусклые."
            " Они будут использоваться на сайте для подоборок с фильмами. Верни результат в формате JSON:\n"
            "```json\n"
            "{\n"
            '  "color1": "#FF5733",\n'
            '  "color2": "#C70039"\n'
            "}\n"
            "```"
        )
        try:
            response = await self.client.chat.completions.create(
                model="claude-3-haiku-20240307", messages=[{"role": "user", "content": prompt}], temperature=1
            )
            response_text = response.choices[0].message.content
            json_data = self._extract_json_to_dict(response_text)
            if json_data and "color1" in json_data and "color2" in json_data:
                return json_data["color1"], json_data["color2"]
            return "#FFFFFF", "#000000"  # noqa: TRY300
        except Exception as e:
            print(f"GPT Color Generation Error: {e!s}")
            return "#FFFFFF", "#000000"
