import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useToast } from "@/components/Toast";

export function usePaymentSettings() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["payment-settings"],
    queryFn: () => api.get("/payment-settings").then((r) => r.data),
    staleTime: 1000 * 30,
  });

  const handleWsEvent = (event: string, data: Record<string, unknown>) => {
    if (event === "payment.settings.updated") {
      queryClient.setQueryData(["payment-settings"], data.settings);
    }
  };

  const ws = useWebSocket({
    onEvent: handleWsEvent,
    reconnect: true,
  });

  return { ...query, ws };
}

export function useAdminPaymentSettings() {
  return useQuery({
    queryKey: ["admin", "payment-settings"],
    queryFn: () => api.get("/admin/payment-settings").then((r) => r.data),
    enabled: false,
  });
}

export function useUpdatePaymentSettings() {
  const queryClient = useQueryClient();
  const toast = useToast();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => api.patch("/admin/payment-settings", data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payment-settings"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "payment-settings"] });
      toast("Payment settings updated", "success");
    },
    onError: () => {
      toast("Failed to update payment settings", "error");
    },
  });
}
