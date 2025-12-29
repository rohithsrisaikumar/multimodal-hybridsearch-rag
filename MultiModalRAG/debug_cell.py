for i,page in enumerate(doc):
    ## Process text
    text = page.get_text()
    if text.strip():
        ##create temporary doc for splitting
        temp_doc=Document(page_content=text, metadata={"page": i, "type": "text"})
        text_chunks=splitter.split_documents([temp_doc])

        #Embed each chunk using CLIP
        for chunk in text_chunks:
            embedding = embed_text(chunk.page_content)
            all_embeddings.append(embedding)
            all_docs.append(chunk)
    
    ## Process Images
    ## THree Important action:

    ##Convert PDF Images to PIL format
    ## Store as Base64 for GPT-4V (which needs base64 images)
    ## Create CLIP embedding for retrieval

    for img_index, img in enumerate(page.get_images(full=True)):
        try: 
            xref=img[0]
            base_image=doc.extract_image(xref)
            image_bytes=base_image["image"]

            # Convert to PIL Image
            pil_image=Image.open(io.BytesIO(image_bytes)).convert("RGB")

            #Create unique identfier
            image_id = f"page_{i}_img_{img_index}"

            # Store image as base64 for later use with GPT-4V
            buffered = io.BytesIO()
            pil_image.save(buffered, format="PNG")
            img_base64=base64.b64encode(buffered.getvalue()).decode()
            image_data_store[image_id]=img_base64

            # Embed image using CLIP
            embedding=embed_images(pil_image)
            all_embeddings.append(embedding)

            # Create document for image
            image_doc=Document(
                page_content=f"[Image: {image_id}]",
                metadata={"page": i, 
                          "type": "image",
                          "image_id": image_id
                        }
            )
            all_docs.append(image_doc)

        except Exception as e:
            print(f"Error processing image {img_index} on page {i} : {e}")
            continue
    
    doc.close()
    