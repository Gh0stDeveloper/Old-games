package ghost.diamondrush.fan;

/**
 * Entry point called by the ORIGINAL main-menu action dispatch (N(), selection=4).
 * Until a real libGDX EnginePort is attached, keep original leaderboard behavior
 * as a safe fallback. CI release gates MUST reject this partial implementation.
 */
public final class FanMenuEntry {
    private static volatile FanRuntimeAdapter adapter;
    private FanMenuEntry(){}
    public static void bind(FanRuntimeAdapter installed) {
        if(installed==null) throw new NullPointerException("installed");
        adapter=installed;
    }
    public static void unbind() {adapter=null;}
    public static boolean tryOpen(){
        FanRuntimeAdapter value=adapter;
        if(value==null) return false;
        value.onLegacyLeaderboardMenuItemTapped();
        return true;
    }
}
