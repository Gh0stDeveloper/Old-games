package ghost.diamondrush.fan;
import java.io.*;

/** Adapter contract; a real libGDX host MUST connect it to game events. */
public final class FanRuntimeAdapter implements FanNavigationController.GameBridge {
    public interface EnginePort {
        void renderFanWorlds(String[] ids);
        void renderFanStages(String worldId,int unlocked,int count);
        void renderMainMenu();
        boolean supportsWorldIndex(int index);
        long launchWorldLevel(int worldIndex,int stageIndex,String path);
    }
    public enum CompletionReason { EXIT_TRIGGER, DEATH, ABANDONED, DEBUG, UNKNOWN }
    private final EnginePort engine;
    private final FanWorldCatalog catalog;
    private final FanNavigationController controller;
    private long activeRunToken;
    private int activeStageIndex=-1;
    private boolean activeRunCompleted;
    public static FanRuntimeAdapter open(EnginePort engine, InputStream w3, File filesDir)throws IOException{
        if(engine==null||w3==null||filesDir==null)throw new NullPointerException();
        return new FanRuntimeAdapter(engine,FanWorldCatalog.read(w3),new FanProgressStore(filesDir));
    }
    public FanRuntimeAdapter(EnginePort engine,FanWorldCatalog catalog,FanProgressStore progress){
        if(engine==null||catalog==null||progress==null)throw new NullPointerException();
        this.engine=engine;this.catalog=catalog;this.controller=new FanNavigationController(this,catalog,progress);
    }
    public FanNavigationController.Screen screen(){return controller.screen();}
    public void onLegacyLeaderboardMenuItemTapped(){controller.onMainMenuOption("LEVELS FAN");}
    public void onFanWorldTapped(String id){controller.onFanWorldSelected(id);}
    public void onFanStageTapped(int stageOneBased){controller.onFanStageSelected(stageOneBased);}
    public void onBack(){
        if(controller.screen()==FanNavigationController.Screen.IN_LEVEL)
            clearRun();
        controller.back();
    }
    private void clearRun(){activeRunToken=0;activeStageIndex=-1;activeRunCompleted=false;}
    public boolean onEngineLevelFinished(int worldIndex,int stageIndex,long token,CompletionReason reason)throws IOException{
        if(reason!=CompletionReason.EXIT_TRIGGER||worldIndex!=FanWorldRegistry.FAN_WORLD_INDEX||
           stageIndex!=activeStageIndex||token<=0||token!=activeRunToken||
           activeRunCompleted||controller.screen()!=FanNavigationController.Screen.IN_LEVEL)
            return false;
        controller.onStageCompleted();
        activeRunCompleted=true;activeRunToken=0;activeStageIndex=-1;
        return true;
    }
    @Override public void showFanWorlds(String[] ids){engine.renderFanWorlds(ids);}
    @Override public void showFanStages(String id,int unlocked,int count){engine.renderFanStages(id,unlocked,count);}
    @Override public void showMainMenu(){engine.renderMainMenu();}
    @Override public void launchFanLevel(String id,int worldIndex,int stageIndex,String path){
        if(!"lost_city".equals(id)||worldIndex!=FanWorldRegistry.FAN_WORLD_INDEX||
            stageIndex<0||stageIndex>=catalog.levels.size()||
            !FanWorldRegistry.worldAsset(FanWorldRegistry.FAN_WORLD_INDEX).equals(path))
            throw new IllegalArgumentException("Fan level mapping mismatch");
        if(!engine.supportsWorldIndex(worldIndex))
            throw new IllegalStateException("Engine does not yet support fourth world");
        long token=engine.launchWorldLevel(worldIndex,stageIndex,path);
        if(token<=0)throw new IllegalStateException("Engine failed to start fan level");
        activeRunToken=token;activeStageIndex=stageIndex;activeRunCompleted=false;
    }
}
