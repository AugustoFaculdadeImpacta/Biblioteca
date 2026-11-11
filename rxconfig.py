import reflex as rx

config = rx.Config(
    app_name="biblioteca_mais_nova",
    telemetry_enabled=False,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                color_mode="inherit",
                accent_color="blue",
                gray_color="slate",
                radius="large",
            )
        ),
    ]
)