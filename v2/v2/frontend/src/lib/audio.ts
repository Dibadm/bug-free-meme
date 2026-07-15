const sounds: Record<string, string> = {
  ball: "/sounds/ball.mp3",
  countdown: "/sounds/countdown.mp3",
  winner: "/sounds/winner.mp3",
  purchase: "/sounds/purchase.mp3",
  deposit: "/sounds/deposit.mp3",
  withdrawal: "/sounds/withdrawal.mp3",
  notification: "/sounds/notification.mp3",
  buttonClick: "/sounds/button-click.mp3",
  success: "/sounds/success.mp3",
  failure: "/sounds/failure.mp3",
};

type SoundKey = keyof typeof sounds;

class AudioManager {
  private enabled = true;
  private volume = 0.5;
  private loaded = new Set<string>();

  init() {
    if (typeof window === "undefined") return;
  }

  setEnabled(enabled: boolean) {
    this.enabled = enabled;
  }

  setVolume(volume: number) {
    this.volume = Math.max(0, Math.min(1, volume));
  }

  async preload(keys: SoundKey[] = Object.keys(sounds) as SoundKey[]) {
    for (const key of keys) {
      try {
        await fetch(sounds[key], { method: "HEAD" });
        this.loaded.add(key);
      } catch {
        this.loaded.delete(key);
      }
    }
  }

  play(key: SoundKey, options: { loop?: boolean; volume?: number } = {}) {
    if (!this.enabled || !this.loaded.has(key)) return;
    try {
      const audio = new Audio(sounds[key]);
      audio.volume = options.volume ?? this.volume;
      audio.loop = options.loop ?? false;
      audio.play().catch(() => {});
    } catch {
      // ignore audio errors
    }
  }

  stopAll() {
    // HTML5 Audio does not provide a global stop; rely on single-instance playback
  }
}

export const audioManager = new AudioManager();
