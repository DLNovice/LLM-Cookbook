"""
Weather Query Tool - 简易天气查询工具
实际项目中可替换为真实天气 API
"""
import random
from typing import Dict, Any


def get_weather(city: str) -> Dict[str, Any]:
    """
    模拟天气查询工具

    Args:
        city: 城市名称

    Returns:
        包含天气信息的字典
    """
    # 模拟天气数据
    weather_conditions = ["晴朗", "多云", "阴天", "小雨", "大雨", "雪"]
    temperatures = range(15, 30)

    return {
        "city": city,
        "temperature": random.choice(temperatures),
        "condition": random.choice(weather_conditions),
        "humidity": f"{random.randint(40, 80)}%",
        "wind_speed": f"{random.randint(5, 25)}km/h"
    }


def format_weather_response(weather_data: Dict[str, Any]) -> str:
    """
    格式化天气数据为可读字符串

    Args:
        weather_data: 天气数据字典

    Returns:
        格式化的天气信息字符串
    """
    return (
        f"📍 城市：{weather_data['city']}\n"
        f"🌡️ 温度：{weather_data['temperature']}°C\n"
        f"☁️ 天气：{weather_data['condition']}\n"
        f"💧 湿度：{weather_data['humidity']}\n"
        f"💨 风速：{weather_data['wind_speed']}"
    )
