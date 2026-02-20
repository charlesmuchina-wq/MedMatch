import TranslationCoverageDashboard from '@/components/TranslationCoverageDashboard';

/**
 * Admin page for viewing translation coverage across all languages
 * CAPA-002 Implementation
 */
const AdminTranslationCoveragePage = () => {
  return (
    <div className="max-w-7xl mx-auto" data-testid="admin-translation-coverage-page">
      <TranslationCoverageDashboard />
    </div>
  );
};

export default AdminTranslationCoveragePage;
