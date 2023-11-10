import requests

targets = [
    'building_an_interactive_ml_dashboard_in_panel.html',
    'building_custom_panel_widgets_using_reactivehtml.html',
    'datashader_0.13.html',
    'holoplot_announcement.html',
    'hugging_face_template.html',
    'hvplot_0.8.0.html',
    'hvplot_announcement.html',
    'panel_0.10.0.html',
    'panel_0.11.0.html',
    'panel_0.12.0.html',
    'panel_0.13.0.html',
    'panel_0.14.html',
    'panel_0.7.0.html',
    'panel_0.8.0.html',
    'panel_1.3.html',
    'panel_1rc.html',
    'panel_announcement.html',
    'pyviz-holoviz.html',
    'pyviz-scipy-bof-2019.html',
    'release_1.10.html',
    'release_1.13.html',
    'release_1.5.html',
    'survey2022.html',
    'WRONG_TO_CHECK.html',
]

# URL = 'https://blog.holoviz.org/'
URL = 'http://localhost:7246/'

for target in targets:
    r = requests.get(URL + target)
    if not r.ok:
        print('Failed querying:', target)
