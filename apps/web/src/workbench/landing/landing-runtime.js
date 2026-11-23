import * as domain from './landing-domain.js';
export function mountLanding(root,initialLanguage,onLanguageChange){
const cleanups=[];const realWindow=globalThis.window;const realDocument=globalThis.document;
const window={matchMedia:realWindow.matchMedia?realWindow.matchMedia.bind(realWindow):()=>({matches:false,addEventListener(){},removeEventListener(){}}),speechSynthesis:realWindow.speechSynthesis,get innerWidth(){return realWindow.innerWidth;},addEventListener(type,listener,options){realWindow.addEventListener(type,listener,options);cleanups.push(()=>realWindow.removeEventListener(type,listener,options));}};
const document={querySelector:root.querySelector.bind(root),querySelectorAll:root.querySelectorAll.bind(root),body:root,documentElement:root,get activeElement(){return realDocument.activeElement;},addEventListener:root.addEventListener.bind(root)};
  'use strict';
  const $ = selector => document.querySelector(selector);
  const $$ = selector => Array.from(document.querySelectorAll(selector));

  const initialCopy = new Map($$('[data-i18n]').map(el => [el, el.innerHTML]));
  const EN = {
    skip:'Skip to content',previewLabel:'DESIGN PREVIEW · SYNTHETIC EXAMPLES',aboutPreview:'About this preview',navWorkflow:'An everyday workflow',navAI:'Meet your AI team',navControl:'Your control',navDemo:'Explore the demo',
    heroEyebrow:'Your everyday AI business assistant',heroLine1:'Your shop.',heroLine2:'A little more',heroLine3:'in sync.',heroDescription:'Bills, payments and the things your supplier said. Bring them together, find the mismatch, and ask the question that matters.',heroCTA:'Try it for yourself',heroSecondary:'See how it works',promiseVoice:'In your language',promiseEvidence:'Answers with evidence',promiseControl:'You make the call',heroNote:'Beyond keeping the books.<br>A little understanding, too.',
    stageTitle:'Start with one bill',demoData:'Demo data',supplier:'Haque Traders',invoiceRef:'Invoice 41',billDemand:'Supplier demand',billType:'Goods account',onePage:'Page 1 of 1',exampleRecord:'SYNTHETIC RECORD',paymentLabel:'Payment for this bill',paymentUnclear:'Already deducted?',returnLabel:'Accepted return credit',returnNotIncluded:'Not yet deducted',railRead:'Read the bill',railMatch:'Match evidence',railAsk:'Ask clearly',questionKicker:'One answer makes it clearer',caseQuestion:'Was the ৳4,000 payment already deducted from this demand?',replyIncluded:'Already deducted',replyNotIncluded:'Not deducted yet',replyUnknown:'Not sure',resultOpen:'Two possibilities remain',supportLimited:'Limited support',stageCaption:'Process illustration · no live AI',motionPause:'Pause motion',
    stripIntro:'Useful AI. On your terms.',stripSource:'Evidence behind the answer',stripUnknown:'Questions when facts are missing',stripApproval:'Approval stays with you',
    workflowKicker:'BUILT AROUND YOUR DAY',workflowTitle:'From opening up<br>to closing the books.',workflowDescription:'Less scattered information. The right evidence and the next useful step, together where you work.',buyTitle:'Understand before you buy.',buyDescription:'Compare prices, offers and credit terms.',receiveTitle:'Check what actually arrived.',receiveDescription:'From a shortage to the credit follow-up.',closeTitle:'Make room for tomorrow.',closeDescription:'Today’s money, tomorrow’s tasks.',
    aiKicker:'INTELLIGENCE YOU CAN FOLLOW',aiTitle:'One question.<br>The right team for the job.',aiDescription:'Reading a bill, finding an old agreement, checking a mismatch. Work is divided when it helps, and the source stays within reach.',memoryTitle:'A conversation with your records',memoryDescription:'Find relevant documents by words and meaning, with sources behind the answer.',workspaceTitle:'The Shongoti workbench',illustration:'Process example',coordinator:'Understand the task',coordinatorTask:'Which question is still open on this bill?',agentReader:'Read the bill',agentMatcher:'Match the terms',agentVerifier:'Check evidence',workspaceFootnote:'Select a role to inspect an example finding. No live agents run here.',
    copilotKicker:'JUST ASK SHONGOTI',copilotTitle:'Start with the words<br>you already use.',copilotDescription:'A question should not get lost in a menu. Move from a question to its evidence, and from evidence to the next step.',voiceCaption:'Your day at a glance. Or out loud.',voiceButton:'Listen to an example brief',voiceHint:'Uses an available device voice, with a text fallback.',copilotName:'Shongoti assistant',copilotMode:'Interactive example · no AI/API calls',chatInitialQuestion:'How much remains on this bill?',sourceInvoice:'Invoice 41',sourcePayment:'Payment',sourceReturn:'Return credit',promptBalance:'How much remains?',promptMissing:'What is unknown?',promptNext:'What happens next?',chatContext:'Answers use only this synthetic case',
    controlKicker:'AI ASSISTS. YOU DECIDE.',controlTitle:'Clear evidence.<br>Your own decision.',control1:'Open the record behind an answer.',control2:'Keep a question open when a critical fact is missing.',control3:'Review a proposal before approving it.',
    faqKicker:'A FEW THINGS WORTH ASKING',faqTitle:'Before you begin.',faqDescription:'The useful details, in plain language.',faq1q:'Is real AI running in this preview?',faq1a:'This is an isolated landing-page design preview. Synthetic facts and explicit rules power the interactions. No model, banking or payment API is called.',faq2q:'Why ask a question if there is a payment receipt?',faq2a:'A payment belonging to a bill and a supplier already deducting it from the latest demand are separate facts. Checking inclusion prevents deducting the same payment twice.',faq3q:'What does the confidence score mean?',faq3a:'Here it is an evidence-support index, not a probability that AI is correct. A critical unknown caps it. A high score never authorizes a payment or ledger adjustment.',faq4q:'Should I enter my real business records here?',faq4a:'Do not enter real bills or personal information in this preview. It has no upload or account connection. Actual product integration is separate work.',finalKicker:'YOUR WORK, YOUR LANGUAGE',finalTitle:'Don’t just keep the books.<br>Make sense of them.',finalCTA:'Change an answer in the demo',finalNote:'One answer can change the next useful step.',footerLine:'For the everyday business of Bangladesh.',motionSetting:'Turn off motion',dialogDone:'Got it'
  };
  let language = 'bn', reply = 'unknown', workflow = 'buy', agent = 'reader', prompt = 'balance';
  let motionPaused = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let lastDialogTrigger = null;
  let activeSpeech = null;
  const text = (bn, en) => language === 'bn' ? bn : en;
  const money = paisa => '৳' + new Intl.NumberFormat(language === 'bn' ? 'bn-BD' : 'en-BD', { maximumFractionDigits: 0 }).format(paisa / 100);
  const current = () => domain.resolveCase(reply);
  const icon = id => '<svg class="icon" aria-hidden="true"><use href="#i-' + id + '"/></svg>';

  function announce(value) { $('#announcement').textContent = value; }
  function refreshCase() {
    const result = current();
    $$('[data-reply]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.reply === reply)));
    $('#result-label').textContent = result.payablePaisa === null ? text('দুটি সম্ভাবনা খোলা', 'Two possibilities remain') : text('নির্বাচিত তথ্য অনুযায়ী বাকি', 'Balance using the selected facts');
    if (result.payablePaisa === null) $('#result-amount').innerHTML = money(result.alternativesPaisa[0]) + ' <span>/</span> ' + money(result.alternativesPaisa[1]);
    else $('#result-amount').textContent = money(result.payablePaisa);
    $('#confidence-word').textContent = result.payablePaisa === null ? text('প্রমাণ সীমিত', 'Limited support') : text('প্রমাণের সমর্থন', 'Evidence support');
    $('#confidence-score').textContent = new Intl.NumberFormat(language === 'bn' ? 'bn-BD' : 'en').format(result.supportIndex) + '/' + text('১০০', '100');
    $('#confidence-chip').classList.toggle('limited', result.payablePaisa === null);
    $('#case-question-title').textContent = text('পেমেন্টের ৪,০০০ টাকা কি আগেই এই দাবি থেকে কাটা হয়েছে?', 'Was the ৳4,000 payment already deducted from this demand?');
  }
  function refreshWorkflow() {
    const title = {
      buy: text('কোন শর্তে কিনবেন?', 'Which offer fits your needs?'),
      receive: text('অর্ডার আর হাতে পাওয়া মাল', 'Ordered and actually received'),
      close: text('দিনশেষের একনজর', 'A view of the day')
    }[workflow];
    let body;
    if (workflow === 'buy') {
      body = '<div class="offer-row"><span class="supplier-avatar">A</span><div class="supplier-info"><strong>' + text('Supplier A', 'Supplier A') + '</strong><small>' + text('আজ cash · একই pack', 'Cash today · same pack') + '</small></div><div class="price">' + money(50000) + '<small>' + text('প্রতি কার্টন', 'per carton') + '</small></div></div>' +
        '<div class="offer-row"><span class="supplier-avatar">B</span><div class="supplier-info"><strong>Supplier B</strong><small>' + text('সাত দিনের বাকি · একই pack', 'Seven days credit · same pack') + '</small></div><div class="price">' + money(51000) + '<small>' + text('প্রতি কার্টন', 'per carton') + '</small></div></div>' +
        '<div class="mock-insight">' + icon('chat') + '<p>' + text('কম দামই একমাত্র শর্ত নয়। কিনলে আগামীকালের cash খরচে কী প্রভাব পড়বে, সেটিও দেখুন।', 'Price is one part of the decision. Check what the purchase leaves for tomorrow’s cash obligations.') + '</p></div>';
    } else if (workflow === 'receive') {
      body = '<div class="mock-receipt-counts"><div class="count-item"><span>' + text('অর্ডার', 'Ordered') + '</span><strong>' + text('১০', '10') + '</strong><small>' + text('কার্টন', 'cartons') + '</small></div><div class="count-item"><span>' + text('পাওয়া গেছে', 'Received') + '</span><strong>' + text('৯', '9') + '</strong><small>' + text('কার্টন', 'cartons') + '</small></div><div class="count-item warning"><span>' + text('অমিল', 'Difference') + '</span><strong>' + text('১', '1') + '</strong><small>' + text('কার্টন', 'carton') + '</small></div></div><div class="upcoming"><span>' + text('সম্ভাব্য দাবি', 'Candidate claim') + '</span><strong>' + money(50000) + '</strong></div><div class="mock-insight">' + icon('chat') + '<p>' + text('এই টাকা এখনই বাকি থেকে কাটবে না। Supplier-এর সম্মতি এবং credit প্রয়োগ আলাদাভাবে নিশ্চিত করতে হবে।', 'This does not reduce the payable yet. Supplier acceptance and application of the credit are separate facts.') + '</p></div>';
    } else {
      body = '<div class="close-totals"><div class="close-total"><span>' + text('হাতে cash', 'Cash on hand') + '</span><strong>' + money(500000) + '</strong></div><div class="close-total"><span>' + text('ডিজিটাল wallet', 'Digital wallet') + '</span><strong>' + money(200000) + '</strong></div></div><div class="upcoming"><span>' + text('কাল ভাড়া · cash প্রয়োজন', 'Rent tomorrow · cash needed') + '</span><strong>' + money(300000) + '</strong></div><div class="mock-insight">' + icon('chat') + '<p>' + text('সব মাধ্যমের টাকা সমানভাবে ব্যবহারযোগ্য নয়। জানা শর্ত আর অজানা তথ্য আলাদা করে পরিকল্পনা করুন।', 'Money in different channels is not always interchangeable. Plan with confirmed constraints and explicit unknowns.') + '</p></div>';
    }
    $('#workflow-panel').innerHTML = '<div class="mock-top"><strong>' + title + '</strong><span class="mock-tag">' + text('উদাহরণ দৃশ্য', 'Example scenario') + '</span></div>' + body;
    $('#workflow-panel').setAttribute('aria-labelledby', 'tab-' + workflow);
    $$('[data-workflow]').forEach(button => {
      const selected = button.dataset.workflow === workflow;
      button.setAttribute('aria-selected', String(selected)); button.classList.toggle('active', selected); button.tabIndex = selected ? 0 : -1;
    });
  }
  function refreshAgent() {
    const data = {
      reader: [text('প্রথমে, যা লেখা আছে।', 'First, what the records say.'), text('চালান ৪১-এ দাবি ২৫,০০০ টাকা। ৪,০০০ টাকার পেমেন্টটি এই bill-এর। এখনো পেমেন্টের prior inclusion জানা দরকার।', 'Invoice 41 demands ৳25,000. The ৳4,000 payment belongs to this bill. Whether the demand already includes it is a separate fact.'), 'invoice'],
      matcher: [text('একই টাকা, আলাদা প্রশ্ন।', 'The same payment. A different question.'), text('৩,০০০ টাকার return credit মেনে নেওয়া হয়েছে, কিন্তু বর্তমান দাবিতে এখনো কাটা হয়নি। পেমেন্ট পাওয়া আর দাবি থেকে কাটা হওয়া এক নয়।', 'The ৳3,000 return credit is accepted and not included in this demand. Acknowledging a payment does not establish prior deduction.'), 'return'],
      verifier: [text('যতটুকু জানা, ততটুকুই সিদ্ধান্ত।', 'Let the evidence set the limit.'), current().payablePaisa === null ? text('পেমেন্ট আগে কাটা হয়েছে কি না অজানা। তাই দুটি অঙ্ক খোলা থাকবে। একই পেমেন্ট দ্বিতীয়বার কাটার সিদ্ধান্ত নেওয়া যাবে না।', 'Prior payment inclusion is unknown. Keep both amounts open instead of making an unsupported second deduction.') : text('প্রিভিউতে আপনার নির্বাচিত উত্তরটি ধরে অঙ্ক হিসাব করা হয়েছে। এই সিদ্ধান্ত এখনো review-এর জন্য; কোনো লেনদেন করা হয়নি।', 'The calculation now uses your selected example reply. It is ready for review; no transaction has been executed.'), 'payment']
    }[agent];
    $('#agent-finding').innerHTML = '<strong>' + data[0] + '</strong><p>' + data[1] + '</p><button class="finding-source" type="button" data-source="' + data[2] + '">' + text('উদাহরণ source দেখুন', 'Inspect the example source') + '</button>';
    $$('[data-agent]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.agent === agent)));
  }
  function answerFor(question) {
    const result = current();
    if (question === 'missing') return result.payablePaisa === null ? text('পেমেন্ট যে দেওয়া হয়েছে, সেটি জানা আছে। অজানা হলো—মহাজন কি বর্তমান ২৫,০০০ টাকার দাবিতে ৪,০০০ টাকা আগেই কেটেছেন? এই উত্তর ছাড়া ২২,০০০ ও ১৮,০০০—দুটিই সম্ভব।', 'The payment event is known. What is missing is whether the supplier already deducted ৳4,000 from the current ৳25,000 demand. Without that fact, both ৳22,000 and ৳18,000 remain possible.') : text('এই উদাহরণে আপনি গুরুত্বপূর্ণ inclusion প্রশ্নের উত্তর বেছে নিয়েছেন। হিসাব সেই উত্তর ধরে হয়েছে; বাস্তব record-এর সত্যতা বা payment execution এটি প্রমাণ করে না।', 'You selected the critical inclusion fact in this example. The arithmetic follows that choice; it does not verify real records or execute a payment.');
    if (question === 'next') return result.payablePaisa === null ? text('মহাজনকে জিজ্ঞেস করুন: “এই ২৫,০০০ টাকার দাবিতে আমার ৪,০০০ টাকার পেমেন্ট আগেই কাটা আছে?” উপরের demo-তে একটি উত্তর বেছে নিয়ে ফল দেখুন।', 'Ask: “Does this ৳25,000 demand already deduct my ৳4,000 payment?” Select a reply in the demo above to see the consequence.') : text('সংশ্লিষ্ট source আর নির্বাচিত উত্তর review করুন। উদাহরণ অনুযায়ী বাকি ', 'Review the sources and the selected reply. The supported example balance is ') + money(result.payablePaisa) + text('। অনুমোদন ছাড়া কোনো action হবে না।', '. No action is authorized by this calculation.');
    if (result.payablePaisa === null) return text('এখনই একটি অঙ্ক নিশ্চিত করা যাবে না। return credit ৩,০০০ টাকা এখনো কাটেনি। কিন্তু পেমেন্ট ৪,০০০ টাকা আগে কাটা হয়েছে কি না অজানা। তাই বাকি ২২,০০০ অথবা ১৮,০০০ টাকা—উত্তরটি আগে দরকার।', 'A single amount is not established yet. The ৳3,000 return credit is not included, but prior inclusion of the ৳4,000 payment is unknown. That leaves ৳22,000 or ৳18,000. The missing answer matters.');
    return reply === 'included' ? text('পেমেন্ট আগেই ধরা হয়েছে, তাই সেটি আবার কাটব না। বর্তমান দাবি ২৫,০০০ থেকে এখনো না-কাটা return credit ৩,০০০ বাদ দিলে বাকি ২২,০০০ টাকা। এটি উদাহরণের অঙ্ক; লেনদেন নয়।', 'The payment was already included, so it must not be deducted again. Deduct only the ৳3,000 return credit from the ৳25,000 demand: ৳22,000 remains. This is example arithmetic, not a transaction.') : text('নির্বাচিত উত্তর অনুযায়ী পেমেন্ট ও return credit—কোনোটিই আগে কাটা হয়নি। ২৫,০০০ থেকে ৪,০০০ ও ৩,০০০ বাদ দিলে বাকি ১৮,০০০ টাকা। বাস্তবে প্রমাণ review ও অনুমোদন আলাদা ধাপ।', 'Your selected reply says neither adjustment was previously included. ৳25,000 minus ৳4,000 and ৳3,000 leaves ৳18,000. Source review and approval remain separate steps.');
  }
  function refreshChat() {
    const questions = {balance:text('এই bill-এ কত টাকা বাকি?', 'How much remains on this bill?'),missing:text('কোন গুরুত্বপূর্ণ তথ্যটি অজানা?', 'Which critical fact is missing?'),next:text('এর পরে কী করা দরকার?', 'What should happen next?')};
    $('#chat-question').textContent = questions[prompt]; $('#chat-answer').textContent = answerFor(prompt);
    $$('[data-prompt]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.prompt === prompt)));
  }
  function refreshMotion() {
    document.body.classList.toggle('motion-paused', motionPaused);
    document.documentElement.style.scrollBehavior = motionPaused ? 'auto' : '';
    $('#motion-toggle').textContent = motionPaused ? text('Motion চালু করুন', 'Enable motion') : text('Motion থামান', 'Pause motion');
    $('#accessibility-motion').textContent = motionPaused ? text('Motion চালু করুন', 'Enable motion') : text('Motion বন্ধ করুন', 'Turn off motion');
    $('#motion-toggle').setAttribute('aria-pressed', String(motionPaused));
    $('#accessibility-motion').setAttribute('aria-pressed', String(motionPaused));
  }
  function setLanguage(value) {
    language = value; document.documentElement.lang = language;
    initialCopy.forEach((bn, el) => { el.innerHTML = language === 'bn' ? bn : (EN[el.dataset.i18n] || bn); });
    $('#language-label').textContent = language === 'bn' ? 'English' : 'বাংলা';
    $('#language-toggle').setAttribute('aria-label', language === 'bn' ? 'Switch to English' : 'বাংলায় দেখুন');
    $('#dialog-close').setAttribute('aria-label', text('বন্ধ করুন', 'Close'));
    $('#menu-toggle').setAttribute('aria-label', text('মেনু খুলুন', 'Open menu'));
    $('.desktop-nav').setAttribute('aria-label', text('প্রধান navigation', 'Main navigation'));
    $('#mobile-nav').setAttribute('aria-label', text('মোবাইল navigation', 'Mobile navigation'));
    $('.bill-paper').setAttribute('aria-label', text('উদাহরণ বিলের প্রমাণ খুলুন', 'Inspect the example invoice'));
    $('.reply-options').setAttribute('aria-label', text('উদাহরণ মহাজনের উত্তর', 'Example supplier reply'));
    $('.workflow-tabs').setAttribute('aria-label', text('দোকানের কাজ', 'Business workflow'));
    $('.agent-selectors').setAttribute('aria-label', text('এজেন্টের কাজ দেখুন', 'Inspect an agent role'));
    $('.prompt-chips').setAttribute('aria-label', text('উদাহরণ প্রশ্ন', 'Example questions'));
    refreshCase(); refreshWorkflow(); refreshAgent(); refreshChat(); refreshMotion();
  }
  function openDialog(kind, trigger) {
    lastDialogTrigger = trigger || document.activeElement;
    let title, kicker, content;
    if (kind === 'invoice') {
      kicker = text('উদাহরণ source', 'EXAMPLE SOURCE'); title = text('চালান ৪১ · হক ট্রেডার্স', 'Invoice 41 · Haque Traders');
      content = '<div class="dialog-source-record"><strong>' + text('বর্তমান দাবি: ২৫,০০০ টাকা', 'Current demand: ৳25,000') + '</strong><p>' + text('এই synthetic bill-এ দাবির অঙ্ক ২৫,০০০ টাকা। পেমেন্ট ও return-এর prior inclusion আলাদা তথ্য।', 'This synthetic bill states a ৳25,000 demand. Prior inclusion of payments and returns must be established separately.') + '</p><p class="doc-note">' + text('পৃষ্ঠা ১ · উদাহরণ তথ্য · বাস্তব নথি নয়', 'Page 1 · synthetic data · not a real document') + '</p></div>';
    } else if (kind === 'payment') {
      kicker = text('উদাহরণ source', 'EXAMPLE SOURCE'); title = text('পেমেন্ট · ৪,০০০ টাকা', 'Payment · ৳4,000');
      content = '<p>' + text('এই পেমেন্ট চালান ৪১-এর জন্য দেওয়া হয়েছে—এটি উদাহরণের নিশ্চিত fact। বর্তমান দাবি থেকে আগে কাটা হয়েছে কি না, সেটি প্রিভিউতে আপনার বাছাই করা উত্তর।', 'The payment belongs to Invoice 41; that is an explicit example fact. Prior inclusion in the current demand is determined by your selected example reply.') + '</p><div class="inline-notice">' + text('পেমেন্ট পাওয়া ≠ বর্তমান দাবি থেকে আগেই কাটা।', 'Payment received does not establish prior deduction.') + '</div>';
    } else if (kind === 'return') {
      kicker = text('উদাহরণ source', 'EXAMPLE SOURCE'); title = text('সম্মত return credit · ৩,০০০ টাকা', 'Accepted return credit · ৳3,000');
      content = '<p>' + text('Supplier এই bill-এর ৩,০০০ টাকার return credit মেনেছে এবং বর্তমান দাবিতে সেটি এখনো কাটেনি—এই দুটি fact উদাহরণে স্পষ্ট করে দেওয়া আছে।', 'The supplier accepted a ৳3,000 return credit for this bill, and it is not included in the current demand. Both are explicit facts in this example.') + '</p><p>' + text('আসল product-এ return পাঠানো, supplier-এর acceptance এবং bill-এ credit প্রয়োগ আলাদা event হবে।', 'In the real product, sending goods back, supplier acceptance and applying a credit are separate events.') + '</p>';
    } else if (kind === 'confidence') {
      kicker = text('স্কোরের ব্যাখ্যা', 'WHY THIS INDEX'); title = text('প্রমাণের সমর্থন, সঠিকতার probability নয়।', 'Evidence support, not a correctness probability.');
      content = '<p>' + text('এখানে পাঁচটি সমান critical claim-এর চারটি শুরুতে supported: base ৮০। পেমেন্টের prior inclusion অজানা থাকায় versioned policy cap ৫৯।', 'Four of five equally weighted critical claims are initially supported: a base of 80. Missing prior payment inclusion caps the index at 59.') + '</p><p>' + text('উদাহরণে আপনি উত্তর বেছে নিলে পাঁচটি claim-ই supported হিসেবে ধরা হয়: index ১০০। এটি বাস্তব প্রমাণ যাচাই, model confidence বা ১০০% সঠিক হওয়ার নিশ্চয়তা নয়।', 'Choosing an example reply supplies the fifth fact, giving an index of 100. This does not verify real evidence, measure model confidence or guarantee correctness.') + '</p><div class="inline-notice">' + text('যে score-ই হোক, অনুমোদন ছাড়া কোনো payment বা হিসাব পরিবর্তন হবে না।', 'No score grants permission to pay or change the ledger.') + '</div>';
    } else {
      kicker = text('শুধু ডিজাইন review', 'DESIGN REVIEW ONLY'); title = text('সংগতি landing preview', 'Shongoti landing preview');
      content = '<p>' + text('এটি আলাদা worktree ও design/landing-preview branch-এর preview। মূল Shongoti app, তার server বা Antigravity-র চলমান code পরিবর্তন করা হয়নি।', 'This preview lives in a separate worktree on design/landing-preview. The main Shongoti application, server and concurrent Antigravity changes are not modified.') + '</p><p>' + text('সব তথ্য synthetic। এখানে real model, RAG, agent, ব্যাংক বা payment API চলে না। পছন্দ হলে পরে design-টি আসল product-এর সঙ্গে সমন্বয় করা যাবে।', 'All facts are synthetic. No live model, RAG, agent, banking or payment API runs here. The design can be integrated with the actual product after review.') + '</p>';
    }
    $('#dialog-kicker').textContent = kicker; $('#dialog-title').textContent = title; $('#dialog-content').innerHTML = content;
    $('#info-dialog').showModal();
  }
  function closeDialog() { $('#info-dialog').close(); }
  function closeMenu() { $('#mobile-nav').hidden = true; $('#menu-toggle').setAttribute('aria-expanded', 'false'); }
  function stopSpeech() { if (activeSpeech && 'speechSynthesis' in window) window.speechSynthesis.cancel(); activeSpeech = null; document.body.classList.remove('voice-playing'); }
  function voiceBrief() {
    if (activeSpeech) { stopSpeech(); return; }
    const transcript = text('এটি সংগতি ডিজাইন প্রিভিউর উদাহরণ brief। ', 'This is an example brief from the Shongoti design preview. ') + answerFor('balance');
    const voices = 'speechSynthesis' in window ? window.speechSynthesis.getVoices() : [];
    const voice = voices.find(v => v.lang.toLowerCase().startsWith(language));
    if (!voice) {
      lastDialogTrigger = $('#voice-brief'); $('#dialog-kicker').textContent = text('লেখায় brief', 'BRIEF TRANSCRIPT'); $('#dialog-title').textContent = text('এই device-এ উপযুক্ত voice পাওয়া যায়নি।', 'A suitable device voice is unavailable.'); $('#dialog-content').textContent = transcript; $('#info-dialog').showModal();
      $('#voice-note').textContent = text('Voice পাওয়া যায়নি। লেখায় brief দেখানো হয়েছে।', 'Voice unavailable. A readable transcript is shown.'); return;
    }
    const utterance = new SpeechSynthesisUtterance(transcript); utterance.voice = voice; utterance.lang = voice.lang; utterance.rate = .95;
    activeSpeech = utterance; document.body.classList.add('voice-playing');
    $('#voice-note').textContent = text('উদাহরণ brief বাজছে। আবার চাপলে থামবে।', 'Playing the example brief. Press again to stop.');
    utterance.onend = () => { activeSpeech = null; document.body.classList.remove('voice-playing'); $('#voice-note').textContent = text('উদাহরণ brief শেষ হয়েছে।', 'The example brief has finished.'); };
    utterance.onerror = () => { activeSpeech = null; document.body.classList.remove('voice-playing'); $('#voice-note').textContent = text('Voice playback হয়নি। সহকারীর লেখায় একই তথ্য পড়তে পারেন।', 'Playback failed. The same facts are available in the written answer.'); };
    window.speechSynthesis.speak(utterance);
  }

  $('#language-toggle').addEventListener('click', () => { stopSpeech(); closeMenu(); setLanguage(language === 'bn' ? 'en' : 'bn'); });
  $$('[data-reply]').forEach(button => button.addEventListener('click', () => {
    reply = button.dataset.reply; refreshCase(); refreshAgent(); refreshChat();
    const result = current(); announce(result.payablePaisa === null ? text('তথ্য অজানা। দুটি সম্ভাবনা খোলা আছে।', 'The critical fact is unknown. Both possibilities remain open.') : text('উদাহরণ অনুযায়ী বাকি ', 'Example balance: ') + money(result.payablePaisa));
    const region = $('.case-result'); region.classList.remove('result-updated'); requestAnimationFrame(() => region.classList.add('result-updated'));
  }));
  $$('[data-workflow]').forEach((button, index, buttons) => {
    button.addEventListener('click', () => { workflow = button.dataset.workflow; refreshWorkflow(); });
    button.addEventListener('keydown', event => {
      let next = null; if (event.key === 'ArrowRight') next = (index + 1) % buttons.length; if (event.key === 'ArrowLeft') next = (index + buttons.length - 1) % buttons.length; if (event.key === 'Home') next = 0; if (event.key === 'End') next = buttons.length - 1;
      if (next !== null) { event.preventDefault(); workflow = buttons[next].dataset.workflow; refreshWorkflow(); buttons[next].focus(); }
    });
  });
  $$('[data-agent]').forEach(button => button.addEventListener('click', () => { agent = button.dataset.agent; refreshAgent(); }));
  $$('[data-prompt]').forEach(button => button.addEventListener('click', () => { prompt = button.dataset.prompt; refreshChat(); }));
  document.addEventListener('click', event => {
    const source = event.target.closest('[data-source]'); if (source) openDialog(source.dataset.source, source);
    const info = event.target.closest('[data-open-dialog]'); if (info) openDialog(info.dataset.openDialog, info);
  });
  $('#dialog-close').addEventListener('click', closeDialog); $('#dialog-done').addEventListener('click', closeDialog);
  $('#info-dialog').addEventListener('close', () => { if (lastDialogTrigger && typeof lastDialogTrigger.focus === 'function') lastDialogTrigger.focus(); });
  $('#info-dialog').addEventListener('click', event => { const r = $('#info-dialog').getBoundingClientRect(); if (event.target === $('#info-dialog') && (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)) closeDialog(); });
  $('#menu-toggle').addEventListener('click', () => { const open = $('#mobile-nav').hidden; $('#mobile-nav').hidden = !open; $('#menu-toggle').setAttribute('aria-expanded', String(open)); });
  $$('#mobile-nav a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(); });
  window.addEventListener('resize', () => { if (window.innerWidth > 760) closeMenu(); });
  ['#motion-toggle', '#accessibility-motion'].forEach(selector => $(selector).addEventListener('click', () => { motionPaused = !motionPaused; refreshMotion(); }));
  $('#voice-brief').addEventListener('click', voiceBrief);
  window.addEventListener('pagehide', stopSpeech);
  setLanguage(initialLanguage);
  root.querySelector('#language-toggle')?.addEventListener('click',()=>onLanguageChange(root.lang));
  return ()=>{cleanups.forEach(fn=>fn());stopSpeech();};
}