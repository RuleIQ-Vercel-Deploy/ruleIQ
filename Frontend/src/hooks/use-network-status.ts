import { useState, useEffect } from "react"

interface NetworkStatus {
  isOnline: boolean
  isSlowConnection: boolean
  connectionType?: string
  effectiveType?: string
}

export function useNetworkStatus() {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({
    isOnline: navigator.onLine,
    isSlowConnection: false,
  })

  useEffect(() => {
    const updateNetworkStatus = () => {
      const connection = (navigator as any).connection || 
                        (navigator as any).mozConnection || 
                        (navigator as any).webkitConnection

      setNetworkStatus({
        isOnline: navigator.onLine,
        isSlowConnection: connection?.effectiveType === "slow-2g" || 
                         connection?.effectiveType === "2g",
        connectionType: connection?.type,
        effectiveType: connection?.effectiveType,
      })
    }

    const handleOnline = () => {
      setNetworkStatus(prev => ({ ...prev, isOnline: true }))
    }

    const handleOffline = () => {
      setNetworkStatus(prev => ({ ...prev, isOnline: false }))
    }

    // Initial check
    updateNetworkStatus()

    // Event listeners
    window.addEventListener("online", handleOnline)
    window.addEventListener("offline", handleOffline)

    // Connection change listener (if supported)
    const connection = (navigator as any).connection
    if (connection) {
      connection.addEventListener("change", updateNetworkStatus)
    }

    return () => {
      window.removeEventListener("online", handleOnline)
      window.removeEventListener("offline", handleOffline)
      if (connection) {
        connection.removeEventListener("change", updateNetworkStatus)
      }
    }
  }, [])

  return networkStatus
}
