import { Link } from "react-router-dom";
import { Shield } from "lucide-react";

const LAST_UPDATED = "June 22, 2026";

const Section = ({ title, children }) => (
  <section className="mt-8">
    <h2 className="text-lg font-semibold text-slate-900 mb-2">{title}</h2>
    <div className="text-sm leading-relaxed text-slate-700 space-y-3">{children}</div>
  </section>
);

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-white" data-testid="privacy-policy-page">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <div className="flex items-center gap-3 mb-2">
          <div className="rounded-2xl bg-gradient-to-br from-turquoise to-cyan-600 p-2.5">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900">Privacy Policy</h1>
        </div>
        <p className="text-sm text-slate-500">Last updated: {LAST_UPDATED}</p>

        <Section title="1. Who we are">
          <p>
            This Privacy Policy describes how the AI KARAU suite — including AI KARAU (webinars/meetings),
            ENZI (messaging), and MedMatch AI (career tools) (collectively, the “Service”) — collects,
            uses, and protects your information. The Service is operated by{" "}
            <strong>[Legal Entity Name]</strong> (“we”, “us”).
          </p>
        </Section>

        <Section title="2. Information we collect">
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Account data:</strong> name, email, and authentication identifiers (e.g. Google or Microsoft sign-in).</li>
            <li><strong>Content you provide:</strong> resumes, messages, meeting titles, transcripts, and files you upload.</li>
            <li><strong>Microsoft/Google data (with your consent):</strong> basic profile and, if granted, read-only calendar data, used only to display your schedule.</li>
            <li><strong>Usage & device data:</strong> log data, error reports, and basic analytics to operate and secure the Service.</li>
          </ul>
        </Section>

        <Section title="3. How we use your information">
          <ul className="list-disc pl-5 space-y-1">
            <li>To provide and improve the Service (meetings, messaging, job-matching, AI features).</li>
            <li>To authenticate you and keep your account secure.</li>
            <li>To generate AI outputs (summaries, action items) from content you submit.</li>
            <li>To communicate service updates and respond to support requests.</li>
          </ul>
        </Section>

        <Section title="4. AI processing">
          <p>
            Some features use third-party AI providers (e.g. OpenAI, Anthropic, Google) to process content
            you submit, such as transcripts or messages, in order to produce summaries, action items, or
            assistance. We do not sell your data, and Microsoft profile/calendar data is not used to train
            third-party models.
          </p>
        </Section>

        <Section title="5. Data sharing">
          <p>
            We share data only with service providers necessary to run the Service (hosting, AI processing,
            email delivery, payment processing) under appropriate agreements, or where required by law. We do
            not sell personal data.
          </p>
        </Section>

        <Section title="6. Data retention & security">
          <p>
            We retain account and content data while your account is active and delete it on request. Data is
            encrypted in transit (TLS) and protected by access controls, security testing, and monitoring.
            Hosting region: <strong>[Hosting Region]</strong>.
          </p>
        </Section>

        <Section title="7. Your rights">
          <p>
            Depending on your location (e.g. GDPR), you may access, correct, export, or delete your data, and
            withdraw consent. To exercise these rights, contact us at <strong>[privacy@your-domain]</strong>.
            You can manage in-app consent in your account privacy settings.
          </p>
        </Section>

        <Section title="8. Contact">
          <p>
            Questions about this policy: <strong>[privacy@your-domain]</strong>. Security concerns:{" "}
            <strong>[security@your-domain]</strong>.
          </p>
        </Section>

        <div className="mt-10 pt-6 border-t border-slate-200 text-sm">
          <Link to="/legal/terms" className="text-turquoise hover:underline">Terms of Use</Link>
        </div>
      </div>
    </div>
  );
}
