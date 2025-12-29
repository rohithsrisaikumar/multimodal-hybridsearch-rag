def create_multimodal_message(query, retrieved_docs):
    """ Create a message with both text & images for GPT-4V"""
    content=[]

    #Add the query
    content.append({
        "type": "text",
        "text": f"Question: {query}\n\nContext:\n"
    })

    # Separate text & image documents
    text_docs=[doc for doc in retrieved_docs if doc.metadata.get("type")=="text"]
    image_docs=[doc for doc in retrieved_docs if doc.metadata.get("type")=="image"]

    #Add text context
    if text_docs:
        text_content="\n\n".join([
            f"[Page {doc.metadata["page"]}]: {doc.page_content}"
            for doc in text_docs
        ])
        content.append({
            "type": "text",
            "text": f"Text excerpts:\n{text_content}\n"
        })
    
    # Add images
    for doc in image_docs:
        image_id=doc.metadata.get("image_id")
        if image_id and image_id in image_data_store:
            content.append({
                "type": "text",
                "text": f"\n[Image from page {doc.metadata['page']}]:\n"
            })
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data: image/png;base64,{image_data_store[image_id]}"
                }
            })
    
    # Add instruction
    content.append({
        "type": "text",
        "text": "\n\nPlease answer the question based on the provided text & images."
    })

    return HumanMessage(content=content)


