# Assumptions & Undecided Items

## Purpose
This document tracks assumptions made during planning and items that remain undecided. All assumptions should be validated during implementation.

---

## ASSUMPTIONS

### Rate Limiting
**[ASSUMPTION]** Single user workload won't hit Meta API rate limits

**Context:** Meta has rate limits that vary by tier. No rate limiting implementation in MVP.

**Risk:** Medium - Could cause API errors if creating many campaigns rapidly

**Validation Needed:** Monitor API responses during implementation. Add rate limiting if errors occur.

**Mitigation:** If needed, add simple rate limiting using time.sleep() between API calls

---

### Video Processing
**[ASSUMPTION]** User will provide properly formatted 16:9 videos

**Context:** No aspect ratio validation in MVP (requires video processing library like opencv or ffmpeg)

**Risk:** Low - User is experienced and will validate videos manually

**Validation Needed:** Check if incorrectly formatted videos cause Meta API errors

**Mitigation:** Add warning in documentation about 16:9 requirement

---

### Concurrent Operations
**[ASSUMPTION]** Sequential processing is sufficient for MVP

**Context:** No concurrent campaign creation. One campaign at a time.

**Risk:** Low - Single user, not creating many campaigns simultaneously

**Validation Needed:** Assess if parallelization needed based on usage patterns

**Mitigation:** APScheduler handles concurrent job execution for scheduled activations

---

### Meta API Version
**[ASSUMPTION]** Using Meta API v18.0 is stable and sufficient

**Context:** Plan specifies v18.0 for base URL

**Risk:** Low - Version should remain stable during MVP development

**Validation Needed:** Verify v18.0 supports all required features (OUTCOME_SALES, Advantage+)

**Mitigation:** Can upgrade to newer version if needed

---

### Token Expiration
**[ASSUMPTION]** System user token set to "Never Expire" won't expire

**Context:** User will configure token to never expire

**Risk:** Low - System user tokens can be set to never expire

**Validation Needed:** Confirm token configuration during setup

**Mitigation:** Add error handling for token expiration (error code 190)

---

### System User BM Ownership
**[RESOLVED - CRITICAL]** System User must be created under user's BM for spend attribution

**Context:** User has two BMs in relationship:
- User's BM: `3723515154528570` (Adrite) - owns System User
- Partner BM: `828723616406567` (PARTIPOST PTE. LTD.) - partner relationship

**Meta Platform Limitation:** System Users can only access entities within their own BM, not partner BM entities

**Impact:**
- ✅ API spend credits to user's BM (correct for Tech Partner goals)
- ❌ Cannot use partner BM as Singapore beneficiary
- ✅ Must use user's BM ID as beneficiary instead
- Both options comply with Singapore regulations

**Risk:** None - Resolved by using user's BM ID (`3723515154528570`) as beneficiary

**Validation:** Tested and confirmed - campaigns successfully created with user's BM as beneficiary

---

### Video Upload Success
**[ASSUMPTION]** Video upload to Meta is reliable and doesn't need retry logic

**Context:** Direct API call for video upload without retry

**Risk:** Medium - Network issues could cause upload failures

**Validation Needed:** Monitor upload success rate during implementation

**Mitigation:** Can add retry logic using tenacity if needed

---

### File System Reliability
**[ASSUMPTION]** File system operations (JSON writes) won't fail

**Context:** Using atomic writes (temp file → rename) but no corruption handling

**Risk:** Low - Modern file systems are reliable

**Validation Needed:** Test behavior if disk full or permissions issue

**Mitigation:** Atomic writes protect against partial writes

---

### Timezone Consistency
**[ASSUMPTION]** User's system time is accurate and set to GMT+8

**Context:** APScheduler uses system time for job execution

**Risk:** Low - User controls local development environment

**Validation Needed:** Verify system timezone during setup

**Mitigation:** Document timezone requirement in setup guide

---

### Meta API Error Format
**[ASSUMPTION]** Meta API errors follow documented format with error codes

**Context:** Error handling expects specific error response structure

**Risk:** Low - Meta API is well-documented

**Validation Needed:** Test error scenarios during implementation

**Mitigation:** Add generic error handler as fallback

---

### Single User Usage
**[ASSUMPTION]** Only one user (Julia) will use this system

**Context:** No authentication, no multi-user support

**Risk:** Very Low - MVP is for personal use

**Validation Needed:** None needed for MVP

**Mitigation:** Add authentication if multi-user needed post-MVP

---

## UNDECIDED

### Budget Minimums
**[UNDECIDED]** Whether to validate budget against Meta's minimum requirements

**Context:** Meta has minimum daily budgets that vary by country and objective

**Decision Needed:** Should system validate budget before API call?

**Options:**
1. No validation - Let Meta API return error
2. Add validation with known minimums per currency
3. Fetch minimums from Meta API (if available)

**Recommendation:** Option 1 for MVP - Let Meta API validate. Add validation post-MVP if errors common.

---

### Concurrent Campaign Creation
**[UNDECIDED]** Whether to support creating multiple campaigns in parallel

**Context:** Current design is sequential (one campaign at a time)

**Decision Needed:** Does user need to create multiple campaigns simultaneously?

**Options:**
1. Sequential only (current plan)
2. Allow parallel creation with queue
3. Batch API support

**Recommendation:** Option 1 for MVP. Assess need based on usage patterns.

---

### Video Storage Location
**[UNDECIDED]** Long-term video file management strategy

**Context:** Videos stored in local `creatives/` directory. No cleanup mechanism.

**Decision Needed:** Should system delete videos after upload? Move to archive?

**Options:**
1. Keep all videos indefinitely
2. Delete after successful upload
3. Archive old videos
4. User manages manually

**Recommendation:** Option 4 for MVP - User manages manually. Can add cleanup post-MVP.

---

### Campaign Update Strategy
**[UNDECIDED]** How to handle campaign editing

**Context:** Campaign editing deferred to post-MVP. What fields should be editable?

**Decision Needed:** Which campaign fields can be updated after creation?

**Options:**
1. Status only (PAUSED/ACTIVE)
2. Budget, name, status
3. Full update including creative
4. No updates (create new campaign)

**Recommendation:** Decide during post-MVP based on user needs.

---

### Logging Level
**[UNDECIDED]** Default logging verbosity

**Context:** No logging configuration specified in plan

**Decision Needed:** INFO, DEBUG, or custom per module?

**Options:**
1. INFO for all modules
2. DEBUG during development, INFO in production
3. Configurable via .env

**Recommendation:** Option 2 - DEBUG for development. Change to INFO when stable.

---

### Error Notification Channels
**[UNDECIDED]** How to notify user of campaign failures (post-MVP)

**Context:** Email notifications deferred. What channels to support?

**Decision Needed:** Email, Slack, SMS, or multiple?

**Options:**
1. Email only
2. Slack webhook
3. Multiple channels (configurable)
4. In-app notifications (if web UI built)

**Recommendation:** Decide when implementing notifications post-MVP. Email likely sufficient.

---

### Scheduled Job Retry Strategy
**[UNDECIDED]** What to do if scheduled activation fails

**Context:** Job marked as failed in schedules.json. No automatic retry.

**Decision Needed:** Should system auto-retry failed activations?

**Options:**
1. No retry - manual intervention required (current plan)
2. Retry N times with backoff
3. Retry indefinitely until success
4. User configurable retry policy

**Recommendation:** Option 1 for MVP. Add retry logic post-MVP if failures common.

---

### Campaign Naming Conflicts
**[UNDECIDED]** How to handle duplicate campaign names in Meta

**Context:** Meta allows duplicate campaign names. Our system uses unique internal IDs.

**Decision Needed:** Should system prevent duplicate names in Meta Ads Manager?

**Options:**
1. Allow duplicates (Meta's default behavior)
2. Check for duplicates before creation
3. Append timestamp to name if duplicate
4. Error if duplicate found

**Recommendation:** Option 1 for MVP - Allow duplicates. Meta campaign ID is unique.

---

### Backup Strategy
**[UNDECIDED]** How to backup data/ directory

**Context:** All state in JSON files. No backup mechanism.

**Decision Needed:** Should system auto-backup or user responsibility?

**Options:**
1. User manual backup
2. Automatic backup before writes
3. Git-based backup
4. Cloud sync (Dropbox, etc.)

**Recommendation:** Option 1 for MVP - Document manual backup. Add automation post-MVP.

---

### API Versioning
**[UNDECIDED]** API versioning strategy

**Context:** Using /api/v1 prefix. What about future versions?

**Decision Needed:** How to handle breaking changes?

**Options:**
1. /api/v1, /api/v2, etc.
2. No versioning (internal API)
3. Header-based versioning
4. Deprecation warnings

**Recommendation:** Option 2 for MVP - No versioning needed for single-user system.

---

### Campaign Archive Strategy
**[UNDECIDED]** How to handle archived/deleted campaigns

**Context:** campaigns.json grows over time. No cleanup mechanism.

**Decision Needed:** Should old campaigns be archived or kept forever?

**Options:**
1. Keep all campaigns in campaigns.json
2. Archive old campaigns to separate file
3. Delete campaigns older than X months
4. User manages manually

**Recommendation:** Option 1 for MVP - Keep everything. Add archive post-MVP if file too large.

---

### Geo Targeting Defaults
**[UNDECIDED]** Default targeting if not specified in YAML

**Context:** Plan specifies Singapore as default, but not enforced in design

**Decision Needed:** What should be default geo targeting?

**Options:**
1. Singapore (user's location)
2. No default - require in YAML
3. All countries
4. Account-based default

**Recommendation:** Option 2 - Require in YAML. No implicit defaults.

---

### Video Thumbnail Generation
**[UNDECIDED]** Whether to auto-generate video thumbnails

**Context:** Thumbnail is optional in campaign YAML. Meta can auto-generate.

**Decision Needed:** Should system extract thumbnail from video?

**Options:**
1. User provides thumbnail (current plan)
2. Auto-extract frame from video
3. Meta auto-generates (no thumbnail specified)
4. User choice via config flag

**Recommendation:** Option 3 for MVP - Let Meta auto-generate. Add extraction post-MVP.

---

## Validation Required

Items that need testing/validation during implementation:

1. **Meta API v18.0 compatibility** - Verify all features work on v18.0
2. **Advantage+ campaign creation** - Test full flow creates proper Advantage+ campaign
3. **Multi-currency handling** - Test with SGD, USD, MYR accounts
4. **Video upload reliability** - Monitor success rate, add retry if needed
5. **Scheduling accuracy** - Verify campaigns activate at correct time (GMT+8)
6. **Token longevity** - Confirm "never expire" tokens work as expected
7. **Sync accuracy** - Verify synced data matches Ads Manager
8. **Error handling** - Test all error scenarios and validate error messages
9. **File system operations** - Test atomic writes, disk full scenarios
10. **APScheduler persistence** - Test job survival across service restarts

---

## Questions for User

*All questions resolved during planning*

---

## Notes

- Mark items as **[RESOLVED]** when decision made during implementation
- Add new assumptions as discovered
- Update risk levels based on testing results
- Reference this document when making technical decisions
