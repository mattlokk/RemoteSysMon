package com.matthew.remotesysmon

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import com.matthew.remotesysmon.ui.theme.RemoteSysMonTheme
import kotlinx.coroutines.delay
import java.io.File

// Data classes for JSON parsing (v2.0 format)
data class RemoteSysMonData(
    val stats: SystemStats,
    val appearance: AppearanceSettings,
    val metadata: MetadataInfo
)

data class SystemStats(
    val cpu: CpuStats,
    val memory: MemoryStats,
    val gpu: GpuStats
)

data class CpuStats(
    @SerializedName("cpu_percent") val cpuPercent: Double,
    @SerializedName("cpu_temp_celsius") val cpuTempCelsius: Double,
    @SerializedName("cpu_power_watts") val cpuPowerWatts: Double? = null
)

data class MemoryStats(
    @SerializedName("total_gb") val totalGb: Double,
    @SerializedName("used_gb") val usedGb: Double,
    val percent: Double
)

data class GpuStats(
    @SerializedName("gpu_usage_percent") val gpuUsagePercent: Int,
    @SerializedName("gpu_temp_celsius") val gpuTempCelsius: Double,
    @SerializedName("gpu_power_watts") val gpuPowerWatts: Double? = null
)

data class AppearanceSettings(
    @SerializedName("background_color") val backgroundColor: String,
    @SerializedName("text_color") val textColor: String,
    @SerializedName("accent_color") val accentColor: String,
    @SerializedName("font_size") val fontSize: Int,
    val theme: String,
    @SerializedName("show_graphs") val showGraphs: Boolean,
    @SerializedName("refresh_rate_ms") val refreshRateMs: Int
)

data class MetadataInfo(
    val timestamp: String,
    val version: String,
    val warning: String?
)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        WindowCompat.getInsetsController(window, window.decorView).let { windowInsetsController ->
            windowInsetsController.hide(WindowInsetsCompat.Type.systemBars())
            windowInsetsController.systemBarsBehavior =
                WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }

        setContent {
            RemoteSysMonTheme {
                SystemMonitorScreen(modifier = Modifier.fillMaxSize())
            }
        }
    }
}

@Composable
fun SystemMonitorScreen(modifier: Modifier = Modifier) {
    var monitorData by remember { mutableStateOf<RemoteSysMonData?>(null) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // Auto-refresh
    LaunchedEffect(Unit) {
        while (true) {
            try {
                val data = readSystemStats()
                monitorData = data
                errorMessage = null
            } catch (e: Exception) {
                errorMessage = e.message ?: "Unknown error"
                monitorData = null
            }
            // Use refresh rate from data, or default to 2 seconds
            val refreshDelay = monitorData?.appearance?.refreshRateMs?.toLong() ?: 2000L
            delay(refreshDelay)
        }
    }

    val remoteTheme = monitorData?.appearance?.let { appearance ->
        val colors = if (appearance.theme.equals("dark", ignoreCase = true)) {
            darkColorScheme(
                background = parseColor(appearance.backgroundColor),
                surface = parseColor(appearance.backgroundColor),
                onBackground = parseColor(appearance.textColor),
                onSurface = parseColor(appearance.textColor),
                primary = parseColor(appearance.accentColor),
                onPrimary = parseColor(appearance.backgroundColor),
                onSurfaceVariant = parseColor(appearance.textColor).copy(alpha = 0.7f),
                tertiaryContainer = parseColor(appearance.accentColor).copy(alpha = 0.2f),
                onTertiaryContainer = parseColor(appearance.accentColor)
            )
        } else {
            lightColorScheme(
                background = parseColor(appearance.backgroundColor),
                surface = parseColor(appearance.backgroundColor),
                onBackground = parseColor(appearance.textColor),
                onSurface = parseColor(appearance.textColor),
                primary = parseColor(appearance.accentColor),
                onPrimary = parseColor(appearance.backgroundColor),
                onSurfaceVariant = parseColor(appearance.textColor).copy(alpha = 0.7f),
                tertiaryContainer = parseColor(appearance.accentColor).copy(alpha = 0.2f),
                onTertiaryContainer = parseColor(appearance.accentColor)
            )
        }

        val baseFontSize = appearance.fontSize.sp
        val typography = Typography(
            headlineMedium = MaterialTheme.typography.headlineMedium.copy(fontSize = baseFontSize * 1.75, fontWeight = FontWeight.Bold),
            titleMedium = MaterialTheme.typography.titleMedium.copy(fontSize = baseFontSize * 1.15),
            displaySmall = MaterialTheme.typography.displaySmall.copy(fontSize = baseFontSize * 2.5, fontWeight = FontWeight.Bold),
            bodyLarge = MaterialTheme.typography.bodyLarge.copy(fontSize = baseFontSize),
            labelSmall = MaterialTheme.typography.labelSmall.copy(fontSize = baseFontSize * 0.75)
        )
        Pair(colors, typography)
    }

    MaterialTheme(
        colorScheme = remoteTheme?.first ?: MaterialTheme.colorScheme,
        typography = remoteTheme?.second ?: MaterialTheme.typography
    ) {
        Surface(
            modifier = modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
                    .verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                if (errorMessage != null) {
                    ErrorCard(errorMessage!!)
                } else if (monitorData != null) {
                    val stats = monitorData!!.stats
                    val metadata = monitorData!!.metadata

                    // Timestamp
                    Text(
                        text = "Last updated: ${metadata.timestamp}",
                        style = MaterialTheme.typography.labelSmall,
                        modifier = Modifier.align(Alignment.End)
                    )
                    Spacer(modifier = Modifier.height(16.dp))

                    // Show warning if present
                    if (metadata.warning != null) {
                        WarningCard(metadata.warning)
                        Spacer(modifier = Modifier.height(16.dp))
                    }

                    // CPU Stats
                    Text(
                        text = "CPU",
                        style = MaterialTheme.typography.headlineMedium,
                        modifier = Modifier.align(Alignment.Start)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        StatTile(
                            label = "Usage",
                            value = "%.1f%%".format(stats.cpu.cpuPercent),
                            modifier = Modifier.weight(1f)
                        )
                        StatTile(
                            label = "Temperature",
                            value = "%.1f°C".format(stats.cpu.cpuTempCelsius),
                            modifier = Modifier.weight(1f)
                        )
                    }

                    // CPU Power (if available)
                    if (stats.cpu.cpuPowerWatts != null) {
                        Spacer(modifier = Modifier.height(8.dp))
                        StatTile(
                            label = "CPU Power",
                            value = "%.1f W".format(stats.cpu.cpuPowerWatts),
                            modifier = Modifier.fillMaxWidth()
                        )
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    // GPU Stats
                    Text(
                        text = "GPU",
                        style = MaterialTheme.typography.headlineMedium,
                        modifier = Modifier.align(Alignment.Start)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        StatTile(
                            label = "Usage",
                            value = "${stats.gpu.gpuUsagePercent}%",
                            modifier = Modifier.weight(1f)
                        )
                        StatTile(
                            label = "Temperature",
                            value = "%.1f°C".format(stats.gpu.gpuTempCelsius),
                            modifier = Modifier.weight(1f)
                        )
                    }

                    // GPU Power (if available)
                    if (stats.gpu.gpuPowerWatts != null) {
                        Spacer(modifier = Modifier.height(8.dp))
                        StatTile(
                            label = "GPU Power",
                            value = "%.1f W".format(stats.gpu.gpuPowerWatts),
                            modifier = Modifier.fillMaxWidth()
                        )
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    // RAM Stats
                    Text(
                        text = "RAM",
                        style = MaterialTheme.typography.headlineMedium,
                        modifier = Modifier.align(Alignment.Start)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        StatTile(
                            label = "Usage",
                            value = "%.1f%%".format(stats.memory.percent),
                            modifier = Modifier.weight(1f)
                        )
                        StatTile(
                            label = "Memory",
                            value = "%.1f / %.1f GB".format(stats.memory.usedGb, stats.memory.totalGb),
                            modifier = Modifier.weight(1f)
                        )
                    }

                } else {
                    // Loading state
                    CircularProgressIndicator(
                        modifier = Modifier.padding(32.dp)
                    )
                    Text(
                        text = "Loading system stats...",
                        style = MaterialTheme.typography.bodyLarge
                    )
                }
            }
        }
    }
}

@Composable
fun StatTile(label: String, value: String, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier,
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp).fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = value,
                style = MaterialTheme.typography.displaySmall,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
fun WarningCard(message: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.tertiaryContainer
        )
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "⚠️",
                fontSize = 20.sp,
                modifier = Modifier.padding(end = 8.dp)
            )
            Text(
                text = message,
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onTertiaryContainer
            )
        }
    }
}

@Composable
fun ErrorCard(message: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Error",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onErrorContainer
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = message,
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onErrorContainer
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Make sure the file exists at: /data/local/tmp/system_stats.json",
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onErrorContainer
            )
        }
    }
}

fun parseColor(hex: String): Color {
    return Color(android.graphics.Color.parseColor(hex))
}

// File reading and parsing functions
fun readSystemStats(): RemoteSysMonData {
    val filePath = "/data/local/tmp/system_stats.json"
    val file = File(filePath)

    if (!file.exists()) {
        throw Exception("File not found at $filePath")
    }

    if (!file.canRead()) {
        throw Exception("Cannot read file. Check permissions.")
    }

    val jsonString = file.readText()

    if (jsonString.isEmpty()) {
        throw Exception("File is empty")
    }

    return try {
        Gson().fromJson(jsonString, RemoteSysMonData::class.java)
            ?: throw Exception("Failed to parse JSON")
    } catch (e: Exception) {
        throw Exception("JSON parsing error: ${e.message}")
    }
}
