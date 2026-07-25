from pydantic import BaseModel, Field


class WeatherResult(BaseModel):
    """Clima atual normalizado, no formato devolvido pela tool `get_weather`."""

    city: str = Field(description="Cidade resolvida pela WeatherAPI")
    temperature_c: float = Field(description="Temperatura atual em graus Celsius")
    description: str = Field(description="Descrição textual das condições do tempo")
    humidity: int = Field(description="Umidade relativa do ar em porcentagem")
