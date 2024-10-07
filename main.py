from transifex.api import transifex_api
import requests
import re
import os
import polib
import json
from config import (
    TRANSIFEX_API_TOKEN,
    TRANSIFEX_PROJECT_SLUG,
    TRANSIFEX_ORGANIZATION_SLUG,
    TARGET_LANGUAGE_CODE
)

transifex_api.setup(auth=TRANSIFEX_API_TOKEN)

pattern = re.compile(r':r:([a-zA-Z0-9_]+)>')


def get_organization():
    for o in transifex_api.Organization.all():
        if o.name == TRANSIFEX_ORGANIZATION_SLUG:
            return o
    return None


def save(translation, path="odoo.po"):
    with open(path, 'w') as po:
        for i in translation:
            po.write(i)


def convert_to_json(resource_name, global_json_file="all_translations.jsonl"):
    translated_po_folder = os.path.join(os.getcwd(), "translated_po")
    po_file_path = os.path.join(
        translated_po_folder, f"{resource_name}_translated.po")

    if not os.path.exists(po_file_path):
        print(f"Error: {po_file_path} does not exist.")
        return

    po = polib.pofile(po_file_path)

    json_folder_path = os.path.join(os.getcwd(), "json_translation")
    os.makedirs(json_folder_path, exist_ok=True)

    global_json_file_path = os.path.join(json_folder_path, global_json_file)

    with open(global_json_file_path, 'a', encoding='utf-8') as json_file:
        for entry in po:
            if entry.msgid and entry.msgstr:
                message = {
                    "messages": [
                        {"role": "system", "content": "You are a translator."},
                        {"role": "user", "content": f"Translate the following text to Persian: '{entry.msgid}'"},
                        {"role": "assistant", "content": entry.msgstr}
                    ]
                }
                json_file.write(json.dumps(message, ensure_ascii=False) + '\n')

    print(
        f"Appended translations from {resource_name} to '{global_json_file_path}'")


def upload_files():
    pass


def spilt_translations(translated_content, resource_name):
    po = polib.pofile(translated_content)

    translated_po = polib.POFile()
    untranslated_po = polib.POFile()

    for entry in po:
        if entry.msgstr:
            translated_po.append(entry)
        else:
            untranslated_po.append(entry)

    translated_folder = os.path.join(os.getcwd(), "translated_po")
    untranslated_folder = os.path.join(os.getcwd(), "untranslated_po")

    os.makedirs(translated_folder, exist_ok=True)
    os.makedirs(untranslated_folder, exist_ok=True)

    translated_po.save(os.path.join(translated_folder,
                       f"{resource_name}_translated.po"))
    untranslated_po.save(os.path.join(untranslated_folder,
                         f"{resource_name}_untranslated.po"))

    print(
        f"Saved translated messages to '{os.path.join(translated_folder, f'{resource_name}_translated.po')}'")
    print(
        f"Saved untranslated messages to '{os.path.join(untranslated_folder, f'{resource_name}_untranslated.po')}'")


def get_url():
    organization = get_organization()
    project = organization.fetch("projects").get(slug=TRANSIFEX_PROJECT_SLUG)
    language = transifex_api.Language.get(code=TARGET_LANGUAGE_CODE)
    resources = project.fetch('resources')

    for resource in resources:
        print(resource)
        url = transifex_api.ResourceTranslationsAsyncDownload.download(
            resource=resource, language=language
        )
        translated_content = requests.get(url).text
        print(translated_content)

        if match := pattern.search(str(resource)):
            resource_name = match.group(1)
            spilt_translations(translated_content, resource_name)
            convert_to_json(resource_name)


if __name__ == "__main__":
    get_url()
    upload_files()
