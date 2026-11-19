package ghost.diamondrush.fan;
import java.util.*;

/** Explicit fourth-world contract. Not yet connected to the original DEX. */
public final class FanWorldRegistry {
    public static final int FAN_WORLD_INDEX=3;
    private static final String[] WORLD_ASSETS={"/w0.bin","/w1.bin","/w2.bin","/w3.bin"};
    private static final String[] ROUTE_ASSETS={"/map_angkor.out","/map_scotland.out","/map_tibet.out","/map_fan_levels.out"};
    private static final String[] IDS={"angkor","scotland","tibet","lost_city"};
    public static final String FAN_SAVE_NAMESPACE="diamond_rush_fan_levels_progress.properties";
    private FanWorldRegistry(){}
    public static String worldAsset(int index){check(index);return WORLD_ASSETS[index];}
    public static String routeAsset(int index){check(index);return ROUTE_ASSETS[index];}
    public static String worldId(int index){check(index);return IDS[index];}
    public static boolean isFan(int index){check(index);return index==FAN_WORLD_INDEX;}
    public static List<String> worldIds(){return Collections.unmodifiableList(Arrays.asList(IDS.clone()));}
    private static void check(int index){if(index<0||index>=WORLD_ASSETS.length)throw new IndexOutOfBoundsException("world="+index);}
}
