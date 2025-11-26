## Summary
Previously, wifi_extractor.py stored WiFi passwords in plain text, which posed a security risk if logs or files were exposed. This PR introduces encryption for password storage and ensures decryption only occurs when credentials are actively needed.

## Changes
- Added encryption layer for WiFi password storage
- Implemented secure decryption on demand
- Removed any residual plaintext handling of credentials
- Updated documentation/comments to reflect secure handling

## Impact
- Enhances security by preventing accidental exposure of sensitive data
- Aligns with best practices for credential management
- No functional change for end users; passwords are still retrieved when required

## Testing
- Verified that encrypted passwords can be decrypted correctly during runtime
- Confirmed that no plaintext passwords are written to disk or logs
