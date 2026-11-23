"""Phase 24: Business Help Desk Engine

Maintains official regulatory corpus governance, document vault tracking,
compliance checklist evaluation, and strictly sourced guidance without hallucinated legal claims.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import json
import uuid
from sqlalchemy.orm import Session

from app.persistence.models import (
    BusinessDocumentModel,
    RegulatoryCorpusModel,
)

DEFAULT_CORPUS_RECORDS = [
    {
        "jurisdiction": "BD",
        "topic": "trade_license",
        "title": "সিটি কর্পোরেশন ও পৌরসভা ট্রেড লাইসেন্স নবায়ন বিধিমালা",
        "citation_reference": "স্থানীয় সরকার (সিটি কর্পোরেশন) আইন ২০০৯ ও আদর্শ কর তফসিল",
        "effective_date": "2009-10-15",
        "last_reviewed_date": "2026-07-01",
        "authority_name": "স্থানীয় সরকার বিভাগ / সিটি কর্পোরেশন / পৌরসভা",
        "official_portal_url": "https://etradelicense.gov.bd",
        "content_text": (
            "বাংলাদেশে যেকোনো বৈধ বাণিজ্যিক ব্যবসা পরিচালনার জন্য স্থানীয় কর্তৃপক্ষ (সিটি কর্পোরেশন, পৌরসভা বা ইউনিয়ন পরিষদ) "
            "থেকে ট্রেড লাইসেন্স গ্রহণ বাধ্যতামূলক। ট্রেড লাইসেন্স প্রতি অর্থবছরের ৩০ জুনের মধ্যে নবায়ন করার বিধান রয়েছে, "
            "তবে জরিমানা ছাড়া সাধারণত ৩০ সেপ্টেম্বর পর্যন্ত নবায়নের সময়সীমা প্রদান করা হয়।"
        ),
        "applicability_rules_json": json.dumps({"required_for_all": True}),
    },
    {
        "jurisdiction": "BD",
        "topic": "vat_bin",
        "title": "মূল্য সংযোজন কর ও সম্পূরক শুল্ক আইন ২০১২ (ভ্যাট নিবন্ধন ও টার্নওভার কর)",
        "citation_reference": "মূল্য সংযোজন কর ও সম্পূরক শুল্ক আইন, ২০১২ (ধারা ৪, ৫ ও ধারা ৯)",
        "effective_date": "2019-07-01",
        "last_reviewed_date": "2026-07-01",
        "authority_name": "জাতীয় রাজস্ব বোর্ড (NBR)",
        "official_portal_url": "https://vat.gov.bd",
        "content_text": (
            "বাৎসরিক টার্নওভার ৫০ লাখ টাকার নিম্নে হলে ভ্যাট নিবন্ধন বাধ্যতামূলক নয় (স্বেচ্ছায় নেওয়া যায়)। "
            "বাৎসরিক টার্নওভার ৫০ লাখ টাকা থেকে ৩ কোটি টাকার মধ্যে হলে ৪% হারে টার্নওভার কর প্রযোজ্য। "
            "বাৎসরিক টার্নওভার ৩ কোটি টাকার অধিক হলে পূর্ণাঙ্গ ১৫% ভ্যাট প্রযোজ্য ও ১৩ ডিজিটের ভ্যাট চালান (মূসক-৬.৩) ইস্যু বাধ্যতামূলক।"
        ),
        "applicability_rules_json": json.dumps({"turnover_threshold_min_paisa": 500000000}),  # 50 Lakh BDT
    },
    {
        "jurisdiction": "BD",
        "topic": "income_tax",
        "title": "আয়কর আইন ২০২৩ (বার্ষিক রিটার্ন দাখিল ও টিআইএন)",
        "citation_reference": "আয়কর আইন, ২০২৩ (ধারা ১৬৬ ও ধারা ২৬৪)",
        "effective_date": "2023-07-01",
        "last_reviewed_date": "2026-07-01",
        "authority_name": "জাতীয় রাজস্ব বোর্ড (NBR)",
        "official_portal_url": "https://etaxnbr.gov.bd",
        "content_text": (
            "ব্যবসার নামে ব্যাংক হিসাব খোলা ও ট্রেড লাইসেন্স নবায়নের জন্য ১২ ডিজিটের ই-টিআইএন (e-TIN) বাধ্যতামূলক। "
            "ব্যবসায়ী করদাতাদের প্রতি বছর ৩০ নভেম্বরের (কর দিবস) মধ্যে বিগত অর্থবছরের হিসাবের ভিত্তিতে আয়কর রিটার্ন দাখিল ও "
            "রিটার্ন দাখিলের প্রমাণপত্র (PSR) সংগ্রহ করতে হবে।"
        ),
        "applicability_rules_json": json.dumps({"required_for_all": True}),
    },
    {
        "jurisdiction": "BD",
        "topic": "commercial_lease",
        "title": "দোকান ভাড়া চুক্তি ও জামানত সংরক্ষণ বিধিমালা",
        "citation_reference": "বাড়ি ভাড়া নিয়ন্ত্রণ আইন ১৯৯১ ও সম্পত্তি হস্তান্তর আইন ১৮৮২",
        "effective_date": "1991-05-08",
        "last_reviewed_date": "2026-01-15",
        "authority_name": "সিভিল কোর্ট / পৌর কর্তৃপক্ষ",
        "official_portal_url": "http://bdlaws.minlaw.gov.bd",
        "content_text": (
            "দোকান ভাড়ার ক্ষেত্রে লিখিত ও ৩০০ টাকার নন-জুডিশিয়াল স্ট্যাম্পে চুক্তিপত্র সম্পাদন করা আবশ্যক। "
            "ভাড়া চুক্তিতে মেয়াদ, মাসিক ভাড়া পরিশোধের শেষ তারিখ, অগ্রিম জামানতের পরিমাণ এবং দোকান ছেড়ে দেওয়ার নোটিশ পিরিয়ড স্পষ্ট উল্লেখ থাকতে হবে।"
        ),
        "applicability_rules_json": json.dumps({"applies_to_rented_spaces": True}),
    },
]


class BusinessHelpDeskEngine:
    """Manages document compliance and provides verified primary-source regulatory guidance."""

    @staticmethod
    def ensure_corpus_seeded(db: Session) -> None:
        """Seeds standard authoritative regulatory corpus if empty."""
        count = db.query(RegulatoryCorpusModel).count()
        if count == 0:
            now = datetime.now(timezone.utc)
            for item in DEFAULT_CORPUS_RECORDS:
                corp = RegulatoryCorpusModel(
                    id=str(uuid.uuid4()),
                    jurisdiction=item["jurisdiction"],
                    topic=item["topic"],
                    title=item["title"],
                    citation_reference=item["citation_reference"],
                    effective_date=item["effective_date"],
                    last_reviewed_date=item["last_reviewed_date"],
                    authority_name=item["authority_name"],
                    official_portal_url=item["official_portal_url"],
                    content_text=item["content_text"],
                    applicability_rules_json=item["applicability_rules_json"],
                    is_active=True,
                    created_at=now,
                )
                db.add(corp)
            db.commit()

    @staticmethod
    def get_compliance_checklist(
        db: Session,
        tenant_id: str,
        shop_type: str = "grocery",
        annual_turnover_paisa: int = 0,
    ) -> Dict[str, Any]:
        """
        Evaluates regulatory document compliance checklist for shop.
        Checks required documents vs uploaded documents.
        """
        # Uploaded docs
        docs = db.query(BusinessDocumentModel).filter(
            BusinessDocumentModel.tenant_id == tenant_id
        ).all()
        doc_map = {d.doc_type: d for d in docs}

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        requirements = [
            {
                "key": "trade_license",
                "title_bn": "ট্রেড লাইসেন্স",
                "title_en": "Trade License",
                "mandatory": True,
                "issuing_authority": "সিটি কর্পোরেশন / পৌরসভা",
                "law_ref": "স্থানীয় সরকার আইন ২০০৯",
            },
            {
                "key": "tin_certificate",
                "title_bn": "ই-টিআইএন সনদ ও রিটার্ন প্রমাণ",
                "title_en": "e-TIN & Tax Return Proof",
                "mandatory": True,
                "issuing_authority": "জাতীয় রাজস্ব বোর্ড (NBR)",
                "law_ref": "আয়কর আইন ২০২৩ ধারা ২৬৪",
            },
            {
                "key": "vat_bin_certificate",
                "title_bn": "ভ্যাট বিআইএন নিবন্ধন",
                "title_en": "VAT BIN Registration",
                # Mandatory if turnover >= 50 lakh BDT (500000000 paisa)
                "mandatory": annual_turnover_paisa >= 500000000,
                "issuing_authority": "জাতীয় রাজস্ব বোর্ড (NBR)",
                "law_ref": "মূসক ও সম্পূরক শুল্ক আইন ২০১২ ধারা ৪",
            },
            {
                "key": "lease_agreement",
                "title_bn": "দোকান ভাড়া চুক্তিপত্র",
                "title_en": "Shop Lease Agreement",
                "mandatory": True,
                "issuing_authority": "বাড়িওয়ালা ও নোটারি",
                "law_ref": "সম্পত্তি হস্তান্তর আইন ১৮৮২",
            },
        ]

        evaluated_checklist = []
        all_compliant = True

        for req in requirements:
            doc = doc_map.get(req["key"])
            if not doc:
                status = "missing"
                if req["mandatory"]:
                    all_compliant = False
                expiry = None
            else:
                expiry = doc.expiry_date
                if expiry and expiry < today_str:
                    status = "expired"
                    if req["mandatory"]:
                        all_compliant = False
                elif expiry and expiry < (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d"):
                    status = "expiring_soon"
                else:
                    status = "valid"

            evaluated_checklist.append({
                "doc_type": req["key"],
                "title_bn": req["title_bn"],
                "title_en": req["title_en"],
                "mandatory": req["mandatory"],
                "issuing_authority": req["issuing_authority"],
                "law_ref": req["law_ref"],
                "status": status,
                "expiry_date": expiry,
                "document_id": doc.id if doc else None,
            })

        return {
            "tenant_id": tenant_id,
            "shop_type": shop_type,
            "annual_turnover_bdt": annual_turnover_paisa / 100,
            "all_mandatory_compliant": all_compliant,
            "checklist": evaluated_checklist,
        }

    @staticmethod
    def upload_document(
        db: Session,
        tenant_id: str,
        doc_type: str,
        title: str,
        issuing_authority: str,
        issue_date: Optional[str] = None,
        expiry_date: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> BusinessDocumentModel:
        """Stores or updates a business document record."""
        now = datetime.now(timezone.utc)
        doc = db.query(BusinessDocumentModel).filter(
            BusinessDocumentModel.tenant_id == tenant_id,
            BusinessDocumentModel.doc_type == doc_type,
        ).first()

        if not doc:
            doc = BusinessDocumentModel(
                tenant_id=tenant_id,
                doc_type=doc_type,
                title=title,
                file_path=file_path,
                issuing_authority=issuing_authority,
                issue_date=issue_date,
                expiry_date=expiry_date,
                status="valid",
                created_at=now,
                updated_at=now,
            )
            db.add(doc)
        else:
            doc.title = title
            doc.issuing_authority = issuing_authority
            doc.issue_date = issue_date
            doc.expiry_date = expiry_date
            if file_path:
                doc.file_path = file_path
            doc.updated_at = now

        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def query_sourced_guidance(
        db: Session,
        tenant_id: str,
        query_text: str,
        shop_type: str = "grocery",
        annual_turnover_paisa: int = 0,
    ) -> Dict[str, Any]:
        """
        Retrieves authoritative, primary-sourced guidance.
        Strict invariant: Never invents legal section numbers, tax rates, or deadlines.
        Separates statutory citation from practical advisory.
        If query is outside published corpus, flags escalation_required: True.
        """
        BusinessHelpDeskEngine.ensure_corpus_seeded(db)

        query_lower = query_text.lower()
        matched_corpus = []

        # Keyword mapping to authoritative topics
        topic_match = None
        if any(w in query_lower for w in ["ট্রেড লাইসেন্স", "trade license", "লাইসেন্স", "নবায়ন", "পৌরসভা", "সিটি কর্পোরেশন"]):
            topic_match = "trade_license"
        elif any(w in query_lower for w in ["ভ্যাট", "vat", "bin", "বিআইএন", "টার্নওভার কর", "চালান", "মূসক"]):
            topic_match = "vat_bin"
        elif any(w in query_lower for w in ["আয়কর", "tax", "income tax", "টিন", "tin", "রিটার্ন", "কর দিবস"]):
            topic_match = "income_tax"
        elif any(w in query_lower for w in ["ভাড়া", "lease", "চুক্তি", "জামানত", "দোকান ভাড়া", "অগ্রিম"]):
            topic_match = "commercial_lease"

        if topic_match:
            record = db.query(RegulatoryCorpusModel).filter(
                RegulatoryCorpusModel.topic == topic_match,
                RegulatoryCorpusModel.is_active == True,
            ).first()
            if record:
                matched_corpus.append(record)

        if not matched_corpus:
            return {
                "matched": False,
                "query": query_text,
                "escalation_required": True,
                "advisory_bn": (
                    "আপনার প্রশ্নটির নির্দিষ্ট আইনি বা কর সংক্রান্ত তথ্য আমাদের অনুমোদিত প্রাথমিক ডাটাবেজে পাওয়া যায়নি। "
                    "ভুল তথ্যের ঝুঁকি এড়াতে একজন নিবন্ধিত আইনজীবী বা আয়কর আইনজীবীর (ITP) সাথে সরাসরি পরামর্শ করুন।"
                ),
                "advisory_en": (
                    "This query is outside our verified statutory corpus. "
                    "To prevent incorrect compliance advice, please consult a certified tax professional or lawyer."
                ),
                "citations": [],
            }

        selected = matched_corpus[0]
        return {
            "matched": True,
            "query": query_text,
            "topic": selected.topic,
            "title": selected.title,
            "statutory_text": selected.content_text,
            "citation": {
                "reference": selected.citation_reference,
                "authority": selected.authority_name,
                "effective_date": selected.effective_date,
                "last_reviewed_date": selected.last_reviewed_date,
                "official_portal_url": selected.official_portal_url,
            },
            "escalation_required": False,
            "disclaimer_bn": "উক্ত তথ্য বাংলাদেশ সরকারের বিধিমালা অনুযায়ী সাধারণ নির্দেশনামূলক। আনুষ্ঠানিক আবেদনের পূর্বে সংশ্লিষ্ট দপ্তরে যাচাই করুন।",
            "disclaimer_en": "This information is derived from official statutes for guidance. Verify with respective authorities prior to submission.",
        }
