export const facts = Object.freeze({ demandPaisa: 2500000, paymentPaisa: 400000, acceptedReturnPaisa: 300000, returnAlreadyIncluded: false });
export function resolveCase(value) {
    const reply = ['included', 'not_included', 'unknown'].includes(value) ? value : 'unknown';
    const known = reply !== 'unknown';
    const afterReturn = facts.demandPaisa - facts.acceptedReturnPaisa;
    return Object.freeze({
      reply,
      payablePaisa: known ? afterReturn - (reply === 'not_included' ? facts.paymentPaisa : 0) : null,
      alternativesPaisa: Object.freeze([afterReturn, afterReturn - facts.paymentPaisa]),
      supportIndex: known ? 100 : 59,
      scoreKind: 'evidence_support_index',
      calibratedProbability: null,
      readiness: known ? 'ready_for_review' : 'needs_clarification',
      canExecuteWithoutApproval: false,
      mode: 'synthetic_design_preview'
    });
  }
