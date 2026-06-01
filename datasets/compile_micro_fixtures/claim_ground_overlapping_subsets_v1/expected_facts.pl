claim_ground(SetAlpha, anticipation, reference_alpha, rejected).
legal_citation_detail(SetAlpha, section_102_a_1, statutory_ground, SrcAlphaCitation).
claim_range(SetAlpha, 1, 1, SrcAlpha).
claim_range(SetAlpha, 2, 2, SrcAlpha).
claim_range(SetAlpha, 4, 4, SrcAlpha).
claim_range(SetAlpha, 6, 9, SrcAlpha).
claim_range(SetAlpha, 12, 21, SrcAlpha).
claim_range(SetAlpha, 23, 23, SrcAlpha).
claim_range(SetAlpha, 25, 39, SrcAlpha).

claim_ground(SetBetaAnticipation, anticipation, reference_beta, rejected).
legal_citation_detail(SetBetaAnticipation, section_102_a_1, statutory_ground, SrcBetaAnticipationCitation).
claim_range(SetBetaAnticipation, 1, 1, SrcBetaAnticipation).
claim_range(SetBetaAnticipation, 2, 2, SrcBetaAnticipation).
claim_range(SetBetaAnticipation, 4, 4, SrcBetaAnticipation).
claim_range(SetBetaAnticipation, 6, 9, SrcBetaAnticipation).
claim_range(SetBetaAnticipation, 12, 21, SrcBetaAnticipation).
claim_range(SetBetaAnticipation, 23, 23, SrcBetaAnticipation).
claim_range(SetBetaAnticipation, 25, 27, SrcBetaAnticipation).

claim_ground(SetBetaObviousness, obviousness, reference_beta, rejected).
legal_citation_detail(SetBetaObviousness, section_103, statutory_ground, SrcBetaObviousnessCitation).
claim_range(SetBetaObviousness, 28, 37, SrcBetaObviousness).

review_outcome(SetAlpha, review_board, affirmed, SrcReview).
review_outcome(SetBetaAnticipation, review_board, affirmed, SrcReview).
review_outcome(SetBetaObviousness, review_board, affirmed, SrcReview).
