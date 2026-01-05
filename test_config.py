from src.core.config import config

def test_config_loading():
    print(f"Loaded Port: {config.get('app', {}).get('port')}")
    print(f"Loaded Model Variant: {config.get('models', {}).get('translation', {}).get('variant')}")

if __name__ == "__main__":
    test_config_loading()
