import pynecone as pc


class HelperBotConfig(pc.Config):
    pass


config = HelperBotConfig(
    app_name="helper_bot",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
