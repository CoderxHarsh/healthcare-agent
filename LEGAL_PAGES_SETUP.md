# Legal Pages & Google Verification Setup

## Overview
This document describes the Terms of Service and Privacy Policy pages added to the HealthCare AI Assistant, along with the setup for Google Search Console verification.

## Pages Added

### 1. Terms of Service Page
- **Path**: `frontend/pages/1_Terms_of_Service.py`
- **URL**: `http://localhost:8501/pages/1_Terms_of_Service`
- **Description**: Contains the complete Terms of Service for the HealthCare AI application, including:
  - Acceptance of terms
  - Use license
  - Disclaimers
  - Health disclaimer (important medical notice)
  - Limitations of liability
  - Modifications and governing law

### 2. Privacy Policy Page
- **Path**: `frontend/pages/2_Privacy_Policy.py`
- **URL**: `http://localhost:8501/pages/2_Privacy_Policy`
- **Description**: Contains the complete Privacy Policy, including:
  - Data collection practices
  - Data usage and security measures
  - Third-party services (Google OAuth, Google Calendar API)
  - Data sharing practices
  - User rights (access, correction, deletion)
  - HIPAA compliance notice
  - Contact information

## Navigation
Both pages are accessible from:
- **Home Page (Guest Mode)**: Footer buttons at the bottom
- **Logged-in Users**: Footer buttons below the navigation tabs
- **Back Navigation**: Each page has a "← Back to Home" button to return to the main app

## Google Verification Setup

### Files Created for Verification:

1. **robots.txt**
   - Location: `frontend/robots.txt`
   - Purpose: Allows search engines to crawl the site and locate the sitemap
   - Contains: Sitemap URL reference

2. **sitemap.xml**
   - Location: `frontend/sitemap.xml`
   - Purpose: Lists all important URLs for search engine indexing
   - Includes: Home page, Terms of Service, Privacy Policy

3. **.well-known directory**
   - Location: `frontend/.well-known/`
   - Purpose: Reserved for website verification and metadata files
   - Can contain: Google verification files, Apple verification, etc.

## Steps for Google Search Console Verification

1. **Add Property to Google Search Console**
   - Go to https://search.google.com/search-console
   - Click "Add property"
   - Enter your domain/URL

2. **Choose Verification Method**
   - **HTML file upload**: Place verification file in `.well-known/` directory
   - **DNS record**: Add DNS TXT record (if you have domain access)
   - **HTML tag**: Add meta tag to main page (already shown in app.py)
   - **Google Analytics**: Connect existing Google Analytics account
   - **Google Tag Manager**: Connect existing GTM account

3. **Submit Sitemap**
   - In Google Search Console, go to Sitemaps
   - Submit: `https://yourdomain.com/sitemap.xml`
   - Google will crawl and index all pages

4. **Monitor Indexing**
   - Check "Coverage" report to see which pages are indexed
   - Fix any errors or warnings
   - Monitor Terms of Service and Privacy Policy pages specifically

## Streamlit Multi-Page App Structure

The Streamlit app now uses the multi-page structure:
```
frontend/
├── app.py                          # Main home page
├── pages/
│   ├── 1_Terms_of_Service.py       # Terms of Service page
│   └── 2_Privacy_Policy.py         # Privacy Policy page
├── robots.txt                      # Search engine crawling rules
├── sitemap.xml                     # URL sitemap for search engines
└── .well-known/                    # Verification files directory
```

The numerical prefix (1_, 2_) determines the order in Streamlit's auto-generated navigation.

## Integration with OAuth

Both legal pages are accessible:
- **Before login** (guest mode)
- **After login** (logged-in users)

They do NOT require authentication, making them publicly available for:
- Search engine indexing
- Google verification
- Legal compliance
- User reference

## Content Compliance

The pages include:
- ✅ Full terms and conditions
- ✅ Health disclaimer (important medical notice)
- ✅ Privacy policy with HIPAA notice
- ✅ Data handling practices
- ✅ User rights information
- ✅ Contact information
- ✅ Copyright notice

## Important Notes

1. **HIPAA Compliance**: The Privacy Policy clearly states that the app is NOT HIPAA-compliant and should not be used for protected health information.

2. **Medical Disclaimer**: The Terms of Service includes a prominent medical disclaimer warning users that the service does not replace professional medical advice.

3. **Google OAuth Integration**: Privacy Policy explains the use of Google OAuth and Calendar API for authentication and reminder scheduling.

4. **Third-Party Services**: Clearly discloses use of Google services and backend API.

## Testing

To test the pages locally:
```bash
cd frontend
streamlit run app.py
```

Then navigate to:
- Home page: http://localhost:8501/
- Terms of Service: Click button or go to http://localhost:8501/pages/1_Terms_of_Service
- Privacy Policy: Click button or go to http://localhost:8501/pages/2_Privacy_Policy

## Deployment Considerations

When deploying to production:

1. **Update URLs in sitemap.xml** to use your production domain
2. **Update REDIRECT_URI** in app.py for Google OAuth callback
3. **Set up proper SSL/TLS** (HTTPS)
4. **Submit to Google Search Console** with production domain
5. **Monitor search console** for any crawling or indexing issues
6. **Add Google Analytics** for traffic tracking (optional)
7. **Add meta descriptions** to pages if needed
8. **Test mobile compatibility** with Google Mobile-Friendly Test

## Next Steps

- [ ] Update sitemap.xml with production URL
- [ ] Add production domain to Google Search Console
- [ ] Submit sitemap to Google Search Console
- [ ] Verify Terms of Service and Privacy Policy pages are indexed
- [ ] Add Google Analytics tracking (optional)
- [ ] Monitor search console for issues
- [ ] Test page load times and mobile compatibility
