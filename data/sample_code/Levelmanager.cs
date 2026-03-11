// Manages level loading, spawn points, and win/lose conditions
public class LevelManager : MonoBehaviour {
    public static LevelManager Instance;

    public Transform playerSpawnPoint;
    public Transform grannySpawnPoint;
    public float levelTimeLimit = 120f; // 2 minutes to escape
    private float timeRemaining;
    private bool levelActive = false;

    public string[] levelNames = { "Kitchen", "Hallway", "Basement" };
    public int currentLevelIndex = 0;

    void Awake() {
        if (Instance == null) Instance = this;
        else Destroy(gameObject);
    }

    void Start() {
        timeRemaining = levelTimeLimit;
        levelActive = true;
        SpawnEntities();
    }

    void Update() {
        if (!levelActive) return;

        // Count down the timer
        timeRemaining -= Time.deltaTime;
        if (timeRemaining <= 0) {
            TriggerLevelFail("Time's up!");
        }
    }

    void SpawnEntities() {
        // Place the player and Granny at their designated spawn points
        GameObject player = GameObject.FindWithTag("Player");
        GameObject granny = GameObject.FindWithTag("Granny");

        if (player != null) player.transform.position = playerSpawnPoint.position;
        if (granny != null) granny.transform.position = grannySpawnPoint.position;
    }

    public void TriggerLevelComplete() {
        levelActive = false;
        GameManager.Instance.AddScore(100);
        Debug.Log("Level complete! Loading next level...");
        LoadNextLevel();
    }

    public void TriggerLevelFail(string reason) {
        levelActive = false;
        Debug.Log("Level failed: " + reason);
        GameManager.Instance.TriggerGameOver();
    }

    void LoadNextLevel() {
        currentLevelIndex++;
        if (currentLevelIndex < levelNames.Length) {
            Debug.Log("Loading level: " + levelNames[currentLevelIndex]);
            // UnityEngine.SceneManagement.SceneManager.LoadScene(levelNames[currentLevelIndex]);
        } else {
            Debug.Log("All levels complete! You escaped Granny!");
            GameManager.Instance.TriggerGameOver();
        }
    }
}