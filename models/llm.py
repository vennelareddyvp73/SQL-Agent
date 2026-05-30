import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

load_dotenv()


class LLMProvider(ABC):

    @abstractmethod
    def create_llm(self,model_id: str,temperature: float):
        pass


class OllamaProvider(LLMProvider):

    def create_llm(self,model_id: str,temperature: float):
        return ChatOllama(model=model_id,temperature=temperature)


class HuggingFaceProvider(LLMProvider):

    def create_llm(self,model_id: str,temperature: float):
        hf_token = os.getenv("HF_TOKEN")

        if hf_token is None:
            raise ValueError("HF_TOKEN not found in .env")

        model = HuggingFaceEndpoint(
            repo_id=model_id,
            task="text-generation",
            huggingfacehub_api_token=hf_token
        )

        return ChatHuggingFace(llm=model, temperature=temperature)



class LLMSingleton:

    _instance = None
    _llm = None
    _model_id = None
    _temperature = None

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:

            cls._instance = super(LLMSingleton,cls).__new__(cls)
        return cls._instance

    def get_model(self,provider: LLMProvider,model_id: str,temperature: float = 0):

        if self._llm is None or self._model_id != model_id or self._temperature != temperature:
            self._llm = provider.create_llm(model_id,temperature)
            self._model_id = model_id
            self._temperature = temperature

        return self._llm



def get_llm(provider: LLMProvider,model_id: str,temperature: float = 0):
    return LLMSingleton().get_model(provider,model_id,temperature)


if __name__ == "__main__":
    try:
        hf_provider = HuggingFaceProvider()
        llm = get_llm(provider=hf_provider,model_id="meta-llama/Llama-3.3-70B-Instruct",temperature=0)
        response = llm.invoke("Hello")
        print("\nResponse:\n")
        print(response.content)

    except Exception as e:
        print(f"Error: {e}")