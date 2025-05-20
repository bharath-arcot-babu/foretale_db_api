import os

class Config:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_REGION = os.getenv("PINECONE_REGION")

    #PINECONE_API_KEY = "pcsk_5qn67z_LiEFLXzvayqeFixbPBnnTMQAv6uB6rX2DUCsZrTZMay432XBGMypMjixhzyU3nd"
    #PINECONE_REGION = "us-east-1"
