from app.agui.weather_intent import has_weather_intent, resolve_card_kind, resolve_city


def test_has_weather_intent_requires_weather_words():
    assert has_weather_intent("qual o clima em Lisboa") is True
    assert has_weather_intent("umidade no rio") is True
    assert has_weather_intent("como está o tempo hoje") is True
    assert has_weather_intent("rio de janeiro") is False
    assert has_weather_intent("oi, tudo bem?") is False
    assert has_weather_intent("lisboa") is False


def test_resolve_card_kind_defaults_to_weather():
    assert resolve_card_kind("qual o clima em Lisboa") == "weather"


def test_resolve_card_kind_detects_humidity():
    assert resolve_card_kind("qual a umidade no rio") == "humidity"
    assert resolve_card_kind("humidity in Curitiba") == "humidity"


def test_resolve_city_from_bare_name():
    assert resolve_city("rio de janeiro") == "Rio de Janeiro"


def test_resolve_city_strips_question_words():
    assert resolve_city("qual o clima em lisboa?") == "Lisboa"
    assert resolve_city("umidade em são paulo agora") == "São Paulo"
    assert resolve_city("umidade no rio de janeiro") == "Rio de Janeiro"


def test_resolve_city_falls_back_when_empty():
    assert resolve_city("qual o clima?") == "São Paulo"
