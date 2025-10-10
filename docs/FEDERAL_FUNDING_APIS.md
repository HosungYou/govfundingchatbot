# Federal Funding Data APIs

## Currently Implemented

### 1. NSF (National Science Foundation) ✅
- **API**: https://www.research.gov/awardapi-service/v1/awards.json
- **Status**: Implemented and working
- **Data**: Research awards, grants, PI information
- **Rate Limit**: No strict limit, but use respectful rate
- **Documentation**: https://www.research.gov/common/webapi/awardapisearch-v1.htm

### 2. Grants.gov (All Federal Agencies) ✅
- **API**: XML Download (https://www.grants.gov/xml-extract/)
- **Status**: Partially implemented (URL needs update)
- **Data**: All federal grant opportunities (NSF, NIH, DOE, NASA, etc.)
- **Coverage**: 26+ federal agencies
- **Update Frequency**: Daily
- **Documentation**: https://www.grants.gov/web/grants/xml-extract.html

## Available for Implementation

### 3. NIH (National Institutes of Health) 🟡
- **API**: NIH RePORTER API
  - Endpoint: https://api.reporter.nih.gov/v2/projects/search
  - Documentation: https://api.reporter.nih.gov/
- **Data**: Research projects, grants, publications
- **Rate Limit**: 1000 requests/hour
- **Cost**: Free
- **Implementation Difficulty**: Medium

**Example Request:**
```bash
curl -X POST "https://api.reporter.nih.gov/v2/projects/search" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {
      "fiscal_years": [2024],
      "agencies": ["NIH"]
    },
    "limit": 500
  }'
```

### 4. DOE (Department of Energy) 🟡
- **API**: DOE PAGES API
  - Endpoint: https://www.osti.gov/api/v1/records
  - Documentation: https://www.osti.gov/dataexplorer/api
- **Data**: Research publications, data, awards
- **Rate Limit**: Reasonable use
- **Cost**: Free
- **Implementation Difficulty**: Medium

**DOE also covered by:**
- EERE (Energy Efficiency & Renewable Energy): https://developer.nrel.gov/
- ARPA-E: Available through Grants.gov

### 5. NASA 🟡
- **API**: NASA Grants and Contracts API
  - Endpoint: https://data.nasa.gov/resource/4x2d-rqgq.json
  - Documentation: https://data.nasa.gov/
- **Data**: Grant solicitations, awards
- **Rate Limit**: 1000 requests/day (no token), unlimited with token
- **Cost**: Free
- **Implementation Difficulty**: Easy

**Example Request:**
```bash
curl "https://data.nasa.gov/resource/4x2d-rqgq.json?$limit=100&$where=fiscal_year=2024"
```

### 6. USAJOBS (Federal Job Opportunities) 🟡
- **API**: USAJOBS API
  - Endpoint: https://data.usajobs.gov/api/search
  - Documentation: https://developer.usajobs.gov/
- **Data**: Federal job postings (relevant for career development)
- **Rate Limit**: 100 requests/minute
- **Cost**: Free (requires API key)
- **Implementation Difficulty**: Easy

### 7. SAM.gov (Contract Opportunities) 🟡
- **API**: SAM.gov Opportunities API
  - Endpoint: https://api.sam.gov/opportunities/v2/search
  - Documentation: https://open.gsa.gov/api/opportunities-api/
- **Data**: Federal contract opportunities
- **Rate Limit**: 1000 requests/hour
- **Cost**: Free (requires API key)
- **Implementation Difficulty**: Medium

## Recommended Implementation Strategy

### Phase 1: Current (MVP) ✅
- NSF Awards API ✅
- Grants.gov XML (covers all agencies) ✅

### Phase 2: High-Value Additions
1. **NIH RePORTER** - Health research (largest funding source)
2. **NASA Data** - Space/science grants
3. **DOE EERE** - Clean energy grants

### Phase 3: Specialized Sources
1. **SAM.gov** - Contract opportunities
2. **USAJOBS** - Federal positions
3. **State-level funding** (requires state-by-state implementation)

## Coverage Comparison

| Agency | Annual Funding | Grants.gov | Dedicated API | Priority |
|--------|----------------|------------|---------------|----------|
| NSF | $8.8B | ✅ | ✅ (implemented) | ⭐⭐⭐ |
| NIH | $47.5B | ✅ | ✅ (available) | ⭐⭐⭐ |
| DOE | $32.4B | ✅ | ✅ (available) | ⭐⭐ |
| NASA | $25.4B | ✅ | ✅ (available) | ⭐⭐ |
| USDA | $3.2B | ✅ | ❌ | ⭐ |
| DoD | $140B+ | ⚠️ (limited) | ✅ (SAM.gov) | ⭐⭐ |

**Note**: Grants.gov already includes opportunities from all these agencies, so dedicated APIs mainly provide:
- More detailed award history
- Better search capabilities
- Real-time updates
- Publication/citation data

## Legal & Compliance

### ✅ Legal to Use
All federal APIs are:
- **Public domain** - No copyright restrictions
- **Open data** - Encouraged for reuse
- **Free** - No licensing fees

### 📋 Requirements
1. **Attribution** - Credit the source agency
2. **Rate limits** - Respect API throttling
3. **Terms of Service** - Follow each API's ToS
4. **Privacy** - Don't scrape personal information

### ⚠️ Best Practices
- Use respectful rate limiting (even if no hard limit)
- Cache data locally (don't hammer APIs)
- Provide attribution in UI
- Follow robots.txt and API guidelines

## Implementation Priority

For your chatbot, I recommend:

**Keep current:**
- ✅ Grants.gov XML (covers 26 agencies in one source)
- ✅ NSF API (detailed awards data)

**Add if needed:**
- NIH RePORTER (if targeting health/biomedical researchers)
- NASA API (if targeting space/science community)
- SAM.gov (if adding contract opportunities)

**Grants.gov alone covers 90%+ of federal funding opportunities**, so additional APIs are mainly for:
- Richer historical data
- Better search/filtering
- Research impact metrics
- Real-time updates beyond daily XML
