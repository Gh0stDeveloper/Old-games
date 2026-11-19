package ghost.diamondrush.fan;
import java.io.IOException;

/** Navigation contract: must be wired into the libGDX menu before an APK is releasable. */
public final class FanNavigationController {
    public interface GameBridge {
        void showFanWorlds(String[] worldIds);
        void showFanStages(String worldId,int highestUnlocked,int stageCount);
        void launchFanLevel(String worldId,int worldIndex,int stageIndex,String resourcePath);
        void showMainMenu();
    }
    public enum Screen { MAIN_MENU,FAN_WORLDS,FAN_STAGES,IN_LEVEL }
    private final GameBridge bridge;
    private final FanWorldCatalog catalog;
    private final FanProgressStore save;
    private Screen screen=Screen.MAIN_MENU;
    private int activeStage=0;
    public FanNavigationController(GameBridge bridge,FanWorldCatalog catalog,FanProgressStore save){
        if(bridge==null||catalog==null||save==null)throw new NullPointerException();
        this.bridge=bridge;this.catalog=catalog;this.save=save;
    }
    public Screen screen(){return screen;}
    public void onMainMenuOption(String selected){
        if(!"LEVELS FAN".equals(selected))return;
        screen=Screen.FAN_WORLDS;
        bridge.showFanWorlds(new String[]{"lost_city"});
    }
    public void onFanWorldSelected(String world){
        if(screen!=Screen.FAN_WORLDS || !"lost_city".equals(world))
            throw new IllegalStateException("World selection unavailable");
        screen=Screen.FAN_STAGES;
        bridge.showFanStages(world,save.unlocked(world),catalog.levels.size());
    }
    public void onFanStageSelected(int stage){
        if(screen!=Screen.FAN_STAGES || stage<1 || stage>catalog.levels.size() || stage>save.unlocked("lost_city"))
            throw new IllegalStateException("Stage locked or not selected");
        bridge.launchFanLevel("lost_city",3,stage-1,"/w3.bin");
        activeStage=stage;screen=Screen.IN_LEVEL;
    }
    public void onStageCompleted() throws IOException {
        if(screen!=Screen.IN_LEVEL || activeStage==0)throw new IllegalStateException("No active fan level");
        save.complete("lost_city",activeStage,catalog.levels.size());
        activeStage=0;screen=Screen.FAN_STAGES;
        bridge.showFanStages("lost_city",save.unlocked("lost_city"),catalog.levels.size());
    }
    public void back(){
        switch(screen){
            case FAN_WORLDS: screen=Screen.MAIN_MENU;bridge.showMainMenu();break;
            case FAN_STAGES: screen=Screen.FAN_WORLDS;bridge.showFanWorlds(new String[]{"lost_city"});break;
            case IN_LEVEL: activeStage=0;screen=Screen.FAN_STAGES;bridge.showFanStages("lost_city",save.unlocked("lost_city"),catalog.levels.size());break;
            default:break;
        }
    }
}
