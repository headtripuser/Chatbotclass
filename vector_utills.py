def upload_to_vector_store(client, vector_store_id, filename):
    try:
        # Zuerst die Datei hochladen und die file_id abrufen
        with open(filename, "rb") as file_data:
            uploaded_file = client.files.create(
                purpose="assistants",  # oder der passende Zweck
                file=file_data
            )

        file_id = uploaded_file.id
        print(f"Datei hochgeladen. File ID: {file_id}")

        # Die Datei dem Vector Store hinzufügen
        vector_store_file = client.beta.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )

        print(f"Datei erfolgreich in den Vector Store hochgeladen: {vector_store_file}")
        client.beta.vector_stores.update(
            vector_store_id=vector_store_id
        )
        print("Vector store updated.")



    except Exception as e:
        print(f"Fehler beim Hochladen der Datei in den Vector Store: {e}")
