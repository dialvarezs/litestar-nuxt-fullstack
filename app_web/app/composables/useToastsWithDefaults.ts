import { useToast } from 'primevue/usetoast'

export function useToastsWithDefaults() {
  const toast = useToast()

  function showError(summary: string, detail?: string) {
    toast.add({
      severity: 'error',
      summary,
      detail,
      life: 5000,
    })
  }

  function showSuccess(summary: string, detail?: string) {
    toast.add({
      severity: 'success',
      summary,
      detail,
      life: 3000,
    })
  }

  return { showError, showSuccess }
}
