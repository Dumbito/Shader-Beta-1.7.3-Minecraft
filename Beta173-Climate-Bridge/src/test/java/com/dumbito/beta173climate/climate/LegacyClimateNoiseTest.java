package com.dumbito.beta173climate.climate;

import org.junit.jupiter.api.Test;
import java.util.Random;
import static org.junit.jupiter.api.Assertions.*;

final class LegacyClimateNoiseTest {
    @Test
    void javaRandomKeepsTheLegacyGeneratorSequence() {
        assertEquals(0.7275636800328681D, new Random(42L).nextDouble(), 0.0D);
    }

    @Test
    void knownLegacyReferenceValuesArePreserved() {
        assertEquals(0.10756615286025406D, new LegacyClimateNoise(0L).temperatureAt(0, 0), 1.0e-14D);
        assertEquals(1.4942328627451067D, new LegacyClimateNoise(0L).temperatureAt(100, 200), 1.0e-14D);
        assertEquals(-1.9186637877363122D, new LegacyClimateNoise(0L).temperatureAt(-100, -200), 1.0e-14D);
        assertEquals(2.3235507113419764D, new LegacyClimateNoise(-123456789L).temperatureAt(12345, -9876), 1.0e-13D);
    }

    @Test
    void fieldIsDeterministicAndChangesWithSeedAndCoordinates() {
        LegacyClimateNoise a = new LegacyClimateNoise(123456789L);
        LegacyClimateNoise b = new LegacyClimateNoise(123456789L);
        LegacyClimateNoise otherSeed = new LegacyClimateNoise(123456790L);
        double v = a.temperatureAt(-1234, 5678);
        assertEquals(v, b.temperatureAt(-1234, 5678), 0.0D);
        assertNotEquals(v, a.temperatureAt(-1233, 5678));
        assertNotEquals(v, otherSeed.temperatureAt(-1234, 5678));
    }

    @Test
    void negativeCoordinatesAreSupportedAndFinite() {
        LegacyClimateNoise sampler = new LegacyClimateNoise(-987654321L);
        for (int x = -100_000; x <= 100_000; x += 10_000) {
            double t = sampler.temperatureAt(x, -x);
            assertTrue(Double.isFinite(t), "non-finite climate value at " + x);
        }
    }
}
