from fastapi import FastAPI
from app.schemas import ChatRequest, ChatResponse
from app.input_guardrails import run_input_guardrails
from app.output_guardrails import run_output_guardrails
from app.llm_client import get_llm_response

app = FastAPI(title="LLM Guardrails Gateway")


@app.get("/")
def health_check():
    return {"status": "running", "message": "LLM Guardrails Gateway is live"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    user_input = request.user_input

    is_input_safe, input_issues = run_input_guardrails(user_input)

    if not is_input_safe:
        return ChatResponse(
            success=False,
            response=None,
            blocked_reason="Input blocked by guardrails",
            flagged_issues=input_issues
        )

    llm_response = get_llm_response(user_input)
    final_response, output_issues = run_output_guardrails(llm_response)

    is_output_safe = not any("blocked topics" in issue for issue in output_issues)

    if not is_output_safe:
        correction_instruction = (
            "Your previous response touched on a restricted topic. "
            "Please rewrite your answer while strictly avoiding any blocked topics."
        )

        retry_response = get_llm_response(user_input, correction_instruction=correction_instruction)
        retry_final_response, retry_issues = run_output_guardrails(retry_response)

        retry_still_unsafe = any("blocked topics" in issue for issue in retry_issues)

        if retry_still_unsafe:
            return ChatResponse(
                success=True,
                response="I'm unable to provide a safe response to this request right now. Please try rephrasing your question.",
                blocked_reason=None,
                flagged_issues=["Auto-retry failed, safe fallback returned"]
            )

        return ChatResponse(
            success=True,
            response=retry_final_response,
            blocked_reason=None,
            flagged_issues=["Response auto-corrected after first attempt flagged an issue"]
        )

    return ChatResponse(
        success=True,
        response=final_response,
        blocked_reason=None,
        flagged_issues=output_issues if output_issues else None
    )
