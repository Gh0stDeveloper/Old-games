import ghost.diamondrush.fan.*;
import java.io.*;
import java.nio.file.*;

public final class FanBridgeSmokeTest {
    static final class FakeEngine implements FanRuntimeAdapter.EnginePort {
        boolean supports=true;
        int worldsShown,stagesShown,launches;
        public void renderFanWorlds(String[] ids){if(ids.length!=1)throw new AssertionError();worldsShown++;}
        public void renderFanStages(String id,int unlocked,int count){
            if(!"lost_city".equals(id)||count!=1||unlocked!=1)throw new AssertionError();
            stagesShown++;
        }
        public void renderMainMenu(){}
        public boolean supportsWorldIndex(int index){return supports&&index==3;}
        public long launchWorldLevel(int world,int stage,String path){
            if(world!=3||stage!=0||!"/w3.bin".equals(path))throw new AssertionError();
            launches++;return launches+500;
        }
    }
    static void check(boolean condition,String msg){if(!condition)throw new AssertionError(msg);}
    public static void main(String[] args)throws Exception {
        // One synthetic 2x2 stage, 3 layers. No proprietary asset required.
        byte[] world=new byte[2+4+2*2*3];
        world[0]=1;world[1]=1;world[2]=2;world[4]=2;
        Path dir=Files.createTempDirectory("fan-levels-smoke-");
        FakeEngine engine=new FakeEngine();
        FanRuntimeAdapter app=FanRuntimeAdapter.open(engine,new ByteArrayInputStream(world),dir.toFile());
        check(FanWorldRegistry.FAN_WORLD_INDEX==3,"world index");
        check("/w3.bin".equals(FanWorldRegistry.worldAsset(3)),"world path");
        FanMenuEntry.unbind();
        check(!FanMenuEntry.tryOpen(),"unbound engine must preserve legacy fallback");
        FanMenuEntry.bind(app);
        check(FanMenuEntry.tryOpen(),"bound fan menu entry must intercept selection");
        check(app.screen()==FanNavigationController.Screen.FAN_WORLDS,"menu route incorrect");
        app.onFanWorldTapped("lost_city");
        app.onFanStageTapped(1);
        check(app.screen()==FanNavigationController.Screen.IN_LEVEL,"stage not running");
        check(!app.onEngineLevelFinished(3,0,501,FanRuntimeAdapter.CompletionReason.DEATH),"death credited");
        check(!app.onEngineLevelFinished(3,0,999,FanRuntimeAdapter.CompletionReason.EXIT_TRIGGER),"wrong token credited");
        check(!app.onEngineLevelFinished(3,1,501,FanRuntimeAdapter.CompletionReason.EXIT_TRIGGER),"wrong level credited");
        check(app.onEngineLevelFinished(3,0,501,FanRuntimeAdapter.CompletionReason.EXIT_TRIGGER),"valid exit lost");
        check(!app.onEngineLevelFinished(3,0,501,FanRuntimeAdapter.CompletionReason.EXIT_TRIGGER),"double completion");
        check(new FanProgressStore(dir.toFile()).isCompleted("lost_city",1),"progress not persisted");
        // Reject launch when the original motor has no registered world 3.
        app.onBack();
        app.onFanWorldTapped("lost_city");
        engine.supports=false;
        boolean blocked=false;
        try{app.onFanStageTapped(1);}catch(IllegalStateException ok){blocked=true;}
        check(blocked,"unregistered world did not block launch");
        FanMenuEntry.unbind();
        check(!FanMenuEntry.tryOpen(),"unbind must restore no-hook fallback");
        System.out.println("PASS: actual menu callback adapter, world 3 guard, session-scoped exit, isolated persistence");
    }
}
