import { Link } from "react-router-dom";
import { FileText } from "lucide-react";

const LAST_UPDATED = "June 22, 2026";

const Section = ({ title, children }) => (
  <section className="mt-8">
    <h2 className="text-lg font-semibold text-slate-900 mb-2">{title}</h2>
    <div className="text-sm leading-relaxed text-slate-700 space-y-3">{children}</div>
  </section>
);

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-white" data-testid="terms-page">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <div className="flex items-center gap-3 mb-2">
          <div className="rounded-2xl bg-gradient-to-br from-turquoise to-cyan-600 p-2.5">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900">Terms of Use</h1>
        </div>
        <p className="text-sm text-slate-500">Last updated: {LAST_UPDATED}</p>

        <Section title="1. Acceptance of terms">
          <p>
            By accessing or using the AI KARAU suite — AI KARAU, ENZI, and MedMatch AI (the “Service”),
            operated by <strong>AI KARAU</strong> — you agree to these Terms of Use. If you do not
            agree, do not use the Service.
          </p>
        </Section>

        <Section title="2. Eligibility & accounts">
          <p>
            You must be at least 16 years old (or the age of digital consent in your jurisdiction) to use the
            Service. You are responsible for your account credentials and all activity under your account.
          </p>
        </Section>

        <Section title="3. Acceptable use">
          <ul className="list-disc pl-5 space-y-1">
            <li>Do not use the Service unlawfully or to infringe others’ rights.</li>
            <li>Do not upload malware, attempt to breach security, or disrupt the Service.</li>
            <li>Do not record or transcribe meetings without the consent required by applicable law.</li>
            <li>Do not misuse AI features to generate unlawful, harmful, or deceptive content.</li>
          </ul>
        </Section>

        <Section title="4. Your content">
          <p>
            You retain ownership of content you submit. You grant us a limited license to process it solely to
            operate the Service (e.g. transcription, summaries, delivery). You are responsible for having the
            rights and consents needed for content you upload.
          </p>
        </Section>

        <Section title="5. Third-party services">
          <p>
            The Service integrates third parties (e.g. Microsoft, Google, AI providers, payment and video
            infrastructure). Your use of those features may be subject to their terms. We are not responsible
            for third-party services.
          </p>
        </Section>

        <Section title="6. Paid plans">
          <p>
            Certain features may require a paid subscription. Fees, billing cycles, and cancellation terms are
            presented at purchase. Except where required by law, fees are non-refundable.
          </p>
        </Section>

        <Section title="7. Disclaimers & limitation of liability">
          <p>
            The Service is provided “as is” without warranties of any kind. AI outputs may be inaccurate and
            should be reviewed before reliance. To the maximum extent permitted by law, we are not liable for
            indirect or consequential damages.
          </p>
        </Section>

        <Section title="8. Termination">
          <p>
            We may suspend or terminate access for violations of these Terms. You may stop using the Service at
            any time and request account deletion.
          </p>
        </Section>

        <Section title="9. Changes & contact">
          <p>
            We may update these Terms; material changes will be posted here. Questions:{" "}
            <strong>support@aikarau.com</strong>.
          </p>
        </Section>

        <div className="mt-10 pt-6 border-t border-slate-200 text-sm">
          <Link to="/legal/privacy" className="text-turquoise hover:underline">Privacy Policy</Link>
        </div>
      </div>
    </div>
  );
}
