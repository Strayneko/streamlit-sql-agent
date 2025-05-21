from dotenv import load_dotenv
import os
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_aws import ChatBedrock

class MySQLAgent:
    def __init__(self):
         load_dotenv()
         
         self.__provider = os.getenv('PROVIDER', '')
         self.__db_uri = os.getenv('DB_URI', '')
         self.__db = SQLDatabase.from_uri(self.__db_uri)

         match self.__provider:
               case 'bedrock':
                  secret_key = os.getenv('AWS_SECRET_KEY')
                  key_id = os.getenv('AWS_KEY_ID')
                  region = os.getenv('AWS_REGION')
                  self.model = os.getenv('AWS_BEDROCK_MODEL')
                  self.__llm = ChatBedrock(model=self.model, aws_secret_access_key=secret_key, aws_access_key_id=key_id, region=region)
               
               case 'openai':
                  api_key = os.getenv('OPENAI_API_KEY')
                  self.model = os.getenv('OPENAI_MODEL')
                  self.__llm = ChatOpenAI(model=self.model, api_key=api_key)
               case _:
                   raise "Provider is not valid!"

         self.__agent = create_react_agent(self.__llm, self.get_toolkit(), prompt=self.get_system_prompt())
    def get_toolkit(self):
            toolkit = SQLDatabaseToolkit(db=self.__db, llm=self.__llm)
            return toolkit.get_tools()    

    def get_llm_model(self):
          return self.__llm
    
    def get_db_instance(self):
          return self.__db
    
    def get_agent_instance(self):
          return self.__agent
    
    def get_system_prompt(self):
          prompt = """
            You are an agent designed to interact with a SQL database.
            Given an input question, create a syntactically correct {dialect} query to run,
            then look at the results of the query and return the answer.

            You can order the results by a relevant column to return the most interesting
            examples in the database. Never query for all the columns from a specific table,
            only ask for the relevant columns given the question.

            You MUST double check your query before executing it. If you get an error while
            executing a query, rewrite the query and try again.

            DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
            database.

            To start you should ALWAYS look at the tables in the database to see what you
            can query. Do NOT skip this step.

            Then you should query the schema of the most relevant tables.

            Always to convert the result into human readable structure such as list or table.
            Always sort the answer by natural sorting.
            Do NOT Expose the table structure to the user""".format(dialect=self.__db.dialect)
          return prompt