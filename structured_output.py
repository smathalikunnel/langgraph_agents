from dotenv import load_dotenv

_ = load_dotenv()

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from langchain_core.pydantic_v1 import BaseModel, Field


chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
# print(chat.invoke("hi"))

# template = ChatPromptTemplate.from_template("""
# tell me about this country: {country}
#                                  """)

class Country(BaseModel):
    
    capital: str
    population: str = Field(description="does the population exceed 500mn. yes or no")#= Field(description="capital of the country")
    name: str = Field(description="name of the country")
    nuclear_powered: bool = Field(description="does the country have an active commerical or military nuclear programme")

country = input("give the country: ")
template = ChatPromptTemplate.from_messages([
    ("system", "given a country, give information about the country by calling the Country function. if a capital is provided as input, respond with the capital itself, not the country. if any other question is asked, DO NOT call the country function. Instead, respond by saying that you are only programmed to answer questions about capitals "), 
    ("human","{country}")
    ])
structured_chat = chat.with_structured_output(Country)#, include_raw=True)
chain = template | structured_chat
response = chain.invoke({"country":country})
# print(response)
print(response.capital)


