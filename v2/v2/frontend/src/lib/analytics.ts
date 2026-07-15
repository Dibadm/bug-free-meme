import { useQuery } from "@tanstack/react-query";
import { api } from "./api";

export interface LiveAnalytics {
  players_online: number;
  concurrent_rooms: number;
  games_running: number;
  cards_sold: number;
  revenue: number;
  deposits: number;
  withdrawals: number;
  average_session_length: number;
  daily_active_users: number;
  monthly_active_users: number;
  house_profit: number;
  prize_distribution: number;
  average_cards_per_player: number;
  average_room_fill: number;
  average_game_duration: number;
}

export function useLiveAnalytics() {
  return useQuery({
    queryKey: ["live-analytics"],
    queryFn: async (): Promise<LiveAnalytics> => {
      const response = await api.get("/admin/analytics");
      return response.data;
    },
    refetchInterval: 5000,
    staleTime: 0,
  });
}
