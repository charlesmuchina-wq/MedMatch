/**
 * Feature flags for capabilities that are not yet production-grade, so the UI
 * does not over-claim. Flip the corresponding env var to "true" once the real
 * capability actually ships.
 */

/**
 * Meeting *media* end-to-end encryption.
 *
 * WebRTC media is always encrypted in transit (DTLS-SRTP), but true end-to-end
 * encryption — where the SFU/relay cannot access media — is not yet implemented
 * (the backend `/e2ee/*` meeting endpoints are a protocol-string stub). Until it
 * ships, "E2E Encrypted" / "End-to-End Encryption" claims in the meeting UI are
 * gated off. The accurate "Encrypted" (in-transit) badges are left visible.
 *
 * NOTE: chat/DM E2EE (Lumi) is a separate, genuinely-implemented feature and is
 * NOT governed by this flag.
 */
export const MEETING_E2EE_ENABLED =
  process.env.REACT_APP_MEETING_E2EE === 'true';

/**
 * SOC 2 certification. Not certified yet, so SOC 2 trust claims are gated off
 * until certification is in place.
 */
export const SOC2_CERTIFIED =
  process.env.REACT_APP_SOC2_CERTIFIED === 'true';
