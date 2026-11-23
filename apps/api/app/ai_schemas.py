"""Provider output is a proposal. Persisted facts and exact code retain authority."""
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,StrictInt,model_validator

class StrictOutput(BaseModel):
    model_config=ConfigDict(extra='forbid')

class ProposedOperation(StrictOutput):
    type:Literal['debt_collection','cash_sale','credit_sale','expense','supplier_payment','return','unknown']
    party_name:str|None=None
    amount_paisa:StrictInt|None=Field(None,ge=0)
    payment_method:Literal['cash','bkash','nagad','bank','unknown']|None=None
    invoice_ref:str|None=None
    source_quote:str
    missing_fields:list[str]=Field(default_factory=list)

    @model_validator(mode='after')
    def required_review_facts(self):
        missing=list(self.missing_fields)
        if self.amount_paisa is None or self.amount_paisa<=0:missing.append('positive amount')
        if self.type in ('debt_collection','credit_sale','supplier_payment') and not self.party_name:missing.append('party')
        if self.type in ('debt_collection','cash_sale','expense','supplier_payment') and self.payment_method in (None,'unknown'):missing.append('payment account')
        if self.type=='unknown':missing.append('operation type')
        self.missing_fields=list(dict.fromkeys(missing))
        return self

class ExtractedLine(StrictOutput):
    description:str
    quantity_text:str|None=None
    unit_price_paisa:StrictInt|None=Field(None,ge=0)
    line_total_paisa:StrictInt|None=Field(None,ge=0)

class CommercialExtraction(StrictOutput):
    party_name:str|None=None
    invoice_ref:str|None=None
    amount_paisa:StrictInt|None=Field(None,ge=0)
    claim_date:str|None=None
    payment_method:str|None=None
    extracted_text:str
    source_quote:str
    uncertainties:list[str]=Field(default_factory=list)
    line_items:list[ExtractedLine]=Field(default_factory=list)
    operations:list[ProposedOperation]=Field(default_factory=list)

class GroundedAnswer(StrictOutput):
    answer:str
    cited_source_ids:list[str]=Field(default_factory=list)
    missing_facts:list[str]=Field(default_factory=list)
    proposed_operations:list[ProposedOperation]=Field(default_factory=list)
    suggested_page:Literal['cases','sales','money','buying','receiving','stock','demand','planner','reports','evidence','none']='none'
