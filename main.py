import asyncio
import os

from prisma import Prisma
from client import ClientOpenAI
from dotenv import load_dotenv

load_dotenv()

ANALISE_PROMPT = """Dado o seguinte diálogo entre um atendente e um cliente, avalie a satisfação do cliente com o atendimento, levando em consideração a clareza, rapidez e eficácia da resposta. 
Atribua uma nota de 0 a 10, sendo 0 para totalmente insatisfeito e 10 para totalmente satisfeito. 
Responda apenas com o número correspondente e não inclua palavras ou frases adicionais.

Aqui está o diálogo:
 
{messages}
"""

RESUMO_PROMPT = """Resuma a seguinte conversa entre um cliente e um atendente. 
O resumo deve incluir os pontos principais discutidos, qualquer solicitação feita pelo cliente e as ações tomadas pelo atendente.

A conversa é a seguinte: 

{messages}
"""

MELHORIA_PROMPT = """Com base na conversa a seguir entre um cliente e um atendente, sugira maneiras de melhorar o atendimento. 
Considere a clareza das respostas, tempo de resposta, empatia e eficácia na resolução do problema. 

Aqui está a conversa: 

{messages}
"""

async def main():
    prisma = Prisma()

    api_key = os.getenv("API_KEY")
    api_url = os.getenv("API_URL")
    await prisma.connect()
    print("Conectando ao banco de dados")
    messages = await prisma.message.group_by(
        by=["session_id"])

    for group in messages:
        sessions_id = group["session_id"]

        sessions_messages = await prisma.message.find_many(
            where={"session_id": sessions_id},
        )

        # Pegando apenas os conteúdos
        contents = [msg.content for msg in sessions_messages]
        # Seria interessante limitar para nao passar do limite de tokens
        concatenated_messages = "\n".join(contents)

        client = ClientOpenAI(
            api_key=api_key,
            api_url=api_url
        )

        #Analise de satisfação
        satisfaction = client.invoke(
            ANALISE_PROMPT.format(
                messages=concatenated_messages
            )
        )

        #Resumo da conversa
        summary = client.invoke(
            RESUMO_PROMPT.format(
                messages=concatenated_messages
            )
        )

        #Melhoria no atendimento
        improvement = client.invoke(
            MELHORIA_PROMPT.format(
                messages=concatenated_messages
            )
        )

        #Inserir resultados na tabela de analise

        await prisma.analysis.create(
            data={
                "session_id": sessions_id,
                "satisfaction": int(satisfaction),
                "summary": summary,
                "improvement": improvement,
            }
        )

    await prisma.disconnect()

if __name__ == "__main__":
    print("Iniciando análise de mensagens...")
    asyncio.run(main())

