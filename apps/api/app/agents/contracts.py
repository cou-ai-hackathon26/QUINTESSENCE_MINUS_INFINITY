from pydantic import Field
from app.ai_schemas import StrictOutput
from app.ai_schemas import GroundedAnswer
from pydantic import StrictInt

class CaseFacts(StrictOutput):
    payment_applicable:bool|None
    return_accepted:bool|None
    payment_included:bool|None
    return_included:bool|None

class CitedFinding(StrictOutput):
    source_id:str
    claim:str
    quote:str

class SpecialistFinding(StrictOutput):
    summary:str
    case_facts:CaseFacts|None
    findings:list[CitedFinding]=Field(default_factory=list)
    missing_facts:list[str]=Field(default_factory=list)
    questions:list[str]=Field(default_factory=list)

class AgentConclusion(GroundedAnswer):
    case_facts:CaseFacts|None
    payable_options_paisa:list[StrictInt]
