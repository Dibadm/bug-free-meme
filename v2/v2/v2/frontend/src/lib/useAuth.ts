import { useState, useEffect, useCallback } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, getProfile } from "./api";
import { useToast } from "@/components/Toast";

interface User {
  id: string;
  username: string;
  first_name?: string;
  last_name?: string;
  photo_url?: string;
  role: "player" | "admin";
  balance: number;
  created_at: string;
}

interface ProfileUpdate {
  first_name?: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: localStorage.getItem("auth_token"),
    isLoading: true,
    isAuthenticated: false,
  });
  const queryClient = useQueryClient();
  const toast = useToast();

  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: getProfile,
    enabled: !!state.token,
    retry: false,
  });

  useEffect(() => {
    if (state.token && !profileQuery.isLoading) {
      if (profileQuery.data) {
        setState((s) => ({
          ...s,
          user: profileQuery.data as unknown as User,
          isLoading: false,
          isAuthenticated: true,
        }));
      } else if (profileQuery.isError) {
        setState((s) => ({
          ...s,
          user: null,
          token: null,
          isLoading: false,
          isAuthenticated: false,
        }));
        localStorage.removeItem("auth_token");
      }
    } else if (!state.token) {
      setState((s) => ({ ...s, isLoading: false, isAuthenticated: false }));
    }
  }, [state.token, profileQuery.data, profileQuery.isError, profileQuery.isLoading]);

  const loginMutation = useMutation({
    mutationFn: async (initData: string) => {
      const result = await api.post("/auth/validate", { init_data: initData });
      return result.data;
    },
    onSuccess: (data) => {
      const token = data.token || data.access_token;
      if (token) {
        localStorage.setItem("auth_token", token);
        localStorage.setItem("telegram_init_data", data.init_data || "");
      }
      setState((s) => ({
        ...s,
        token,
        isAuthenticated: true,
        isLoading: false,
      }));
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
    onError: () => {
      toast("Login failed. Please try again.", "error");
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async () => {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("telegram_init_data");
    },
    onSettled: () => {
      setState({
        user: null,
        token: null,
        isLoading: false,
        isAuthenticated: false,
      });
      queryClient.clear();
    },
  });

  const updateProfileMutation = useMutation({
    mutationFn: (data: ProfileUpdate) => api.patch("/profile", data),
    onSuccess: (data) => {
      setState((s) => (s.user ? { ...s, user: { ...s.user, ...data } } : s));
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      toast("Profile updated successfully", "success");
    },
    onError: () => {
      toast("Failed to update profile", "error");
    },
  });

  const login = useCallback((initData: string) => {
    loginMutation.mutate(initData);
  }, [loginMutation]);

  const logout = useCallback(() => {
    logoutMutation.mutate();
  }, [logoutMutation]);

  const updateProfile = useCallback((data: ProfileUpdate) => {
    updateProfileMutation.mutate(data);
  }, [updateProfileMutation]);

  return {
    ...state,
    login,
    logout,
    updateProfile,
    isLoggingIn: loginMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    isUpdatingProfile: updateProfileMutation.isPending,
  };
}
