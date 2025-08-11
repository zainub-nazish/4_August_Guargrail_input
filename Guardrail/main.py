from dotenv import load_dotenv
load_dotenv()
from agents import Agent,Runner,function_tool,RunContextWrapper,input_guardrail,GuardrailFunctionOutput
from pydantic import BaseModel

class Account(BaseModel):
    name: str
    pin: int

class Guardrails_output(BaseModel):
    is_not_bank_related :bool


guardrail_agent = Agent(
    name= "Guardrail Agent",
    instructions="Check if the is asking you bank related queries.",
    output_type=Guardrails_output,
)  

@input_guardrail
async def check_bank_related(ctx:RunContextWrapper[None],agent:Agent,input:str) -> GuardrailFunctionOutput:

    result= await Runner.run(guardrail_agent,input,context=ctx.context)

    return GuardrailFunctionOutput(output_info=result.final_output,tripwire_triggered=result.final_output.is_not_bank_related)

def check_user(ctx:RunContextWrapper[Account],agent:Agent)->bool:

    if ctx.context.name == "Asharib" and ctx.context.pin == 1234:
        return True
    else:
        return False
    
@function_tool(is_enabled=check_user)

def check_balance(account_number:str)->str:
    return f"The balance of account is $1000000"

bank_agent = Agent(
    name= "Bank Agent",
    instructions= "You are a bank agent.You help customers with their questions you can use the tools to get the information",
    tools= [check_balance],
    input_guardrails=[check_bank_related]
)

user_context=Account(name="Asharib",pin=1234)

result=Runner.run_sync(bank_agent,"I Want to my check balance my account no is 309473804",context=user_context)

print(result.final_output)




