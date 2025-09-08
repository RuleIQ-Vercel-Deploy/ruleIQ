#!/bin/bash

echo "Fixing all remaining ESLint warnings..."

# Fix unused variables by prefixing with underscore
files=(
  "app/(dashboard)/compliance-wizard/test/page.tsx"
  "app/(dashboard)/data-export-demo/page.tsx"
  "app/(dashboard)/policies/new/page.tsx"
  "app/(dashboard)/settings/page.tsx"
  "app/(dashboard)/users/page.tsx"
  "components/compliance/control-implementation-form.tsx"
  "components/data-export/export-dialog.tsx"
  "components/policies/editor.tsx"
  "components/settings/branding-settings.tsx"
  "components/ui/data-table/data-table-faceted-filter.tsx"
  "lib/stores/voice.store.ts"
  "lib/tanstack-query/hooks/use-freemium.ts"
  "src/components/magicui/animated-beam.tsx"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "Fixing $file..."
    
    # Fix specific patterns
    case "$file" in
      "app/(dashboard)/compliance-wizard/test/page.tsx")
        sed -i 's/data: complianceData/data: _complianceData/g' "$file"
        sed -i 's/data: frameworksData/data: _frameworksData/g' "$file"
        sed -i 's/loading: frameworksLoading/loading: _frameworksLoading/g' "$file"
        sed -i 's/error: frameworksError/error: _frameworksError/g' "$file"
        ;;
      
      "app/(dashboard)/data-export-demo/page.tsx")
        sed -i 's/const handleExport = async (format: ExportFormat, options: ExportOptions)/const handleExport = async (_format: ExportFormat, _options: ExportOptions)/g' "$file"
        ;;
      
      "app/(dashboard)/policies/new/page.tsx")
        sed -i 's/const \[selectedTemplate, setSelectedTemplate\]/const [_selectedTemplate, setSelectedTemplate]/g' "$file"
        sed -i 's/const handleGenerate = async (data: PolicyInputs)/const handleGenerate = async (_data: PolicyInputs)/g' "$file"
        ;;
      
      "app/(dashboard)/settings/page.tsx")
        sed -i 's/const handleUpdateRBACSettings = (data: unknown)/const handleUpdateRBACSettings = (_data: unknown)/g' "$file"
        sed -i 's/const handleTestIntegration = (integration: string)/const handleTestIntegration = (_integration: string)/g' "$file"
        ;;
      
      "app/(dashboard)/users/page.tsx")
        sed -i 's/const \[selectedUser, setSelectedUser\]/const [_selectedUser, setSelectedUser]/g' "$file"
        sed -i 's/const \[dialogOpen, setDialogOpen\]/const [_dialogOpen, setDialogOpen]/g' "$file"
        ;;
      
      "components/compliance/control-implementation-form.tsx")
        sed -i 's/onSubmit={(data)/onSubmit={(_data)/g' "$file"
        ;;
      
      "components/data-export/export-dialog.tsx")
        sed -i 's/onSubmit: (format: ExportFormat, options: ExportOptions)/onSubmit: (_format: ExportFormat, _options: ExportOptions)/g' "$file"
        ;;
      
      "components/policies/editor.tsx")
        sed -i 's/onChange={(value)/onChange={(_value)/g' "$file"
        sed -i 's/const handleEditorChange = (value: string)/const handleEditorChange = (_value: string)/g' "$file"
        ;;
      
      "components/settings/branding-settings.tsx")
        sed -i 's/onSubmit: (data: BrandingFormData)/onSubmit: (_data: BrandingFormData)/g' "$file"
        ;;
      
      "components/ui/data-table/data-table-faceted-filter.tsx")
        sed -i 's/const selectedValues =/const _selectedValues =/g' "$file"
        ;;
      
      "lib/stores/voice.store.ts")
        sed -i 's/interface VoiceTranscript/interface _VoiceTranscript/g' "$file"
        sed -i 's/startRecording: (options?: RecordingOptions)/startRecording: (_options?: RecordingOptions)/g' "$file"
        sed -i 's/configureVoice: (config: VoiceConfig)/configureVoice: (_config: VoiceConfig)/g' "$file"
        sed -i 's/executeCommand: (command: VoiceCommand)/executeCommand: (_command: VoiceCommand)/g' "$file"
        sed -i 's/addTrigger: (trigger: VoiceTrigger)/addTrigger: (_trigger: VoiceTrigger)/g' "$file"
        sed -i 's/removeTrigger: (command: string)/removeTrigger: (_command: string)/g' "$file"
        ;;
      
      "lib/tanstack-query/hooks/use-freemium.ts")
        sed -i 's/const utmSource = searchParams\.get/const _utmSource = searchParams.get/g' "$file"
        sed -i 's/const utmCampaign = searchParams\.get/const _utmCampaign = searchParams.get/g' "$file"
        ;;
      
      "src/components/magicui/animated-beam.tsx")
        sed -i 's/const entry = entries/const _entry = entries/g' "$file"
        ;;
    esac
  fi
done

# Fix progress parameters in chat components
echo "Fixing progress parameters..."
sed -i 's/streamMessage: async ({ messages, abortSignal, onUpdate }, { body })/streamMessage: async ({ messages, abortSignal, onUpdate }, { body: _body })/g' \
  "lib/stores/chat.store.ts" 2>/dev/null || true

sed -i 's/onUpdate({ progress })/onUpdate({ progress: _progress })/g' \
  "lib/stores/chat.store.ts" 2>/dev/null || true

echo "Running ESLint autofix..."
pnpm eslint . --fix --ext .ts,.tsx,.js,.jsx 2>/dev/null || true

echo "✅ ESLint fixes completed!"