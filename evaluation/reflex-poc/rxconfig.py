import reflex as rx
config = rx.Config(
    app_name="reflex_poc",
    frontend_port=3000,
    backend_port=3000,
    backend_host="127.0.0.1",
    api_url="http://127.0.0.1:3000",
    telemetry_enabled=False,
)
