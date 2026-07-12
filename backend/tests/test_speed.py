import time
from core.objective_function import evaluate_helicopter
from core.optimizers import TuningOptimizers

def test_speed():
    print("Testing single evaluation...")
    t0 = time.time()
    # evaluate a single particle
    cost = evaluate_helicopter([10, 1, 1, 10, 1, 1], 0.436, 0.52, t_max=10.0, dt=0.001)
    print(f"Single evaluation took {time.time() - t0:.4f}s. Cost: {cost}")
    
    print("\nTesting parallel PSO...")
    t0 = time.time()
    results = TuningOptimizers.pso_helicopter(
        setpoint_pitch=0.436, 
        setpoint_yaw=0.52, 
        n_particles=20, 
        iters_list=[5], 
        t_max=10.0
    )
    print(f"Parallel PSO (5 iters, 20 particles) took {time.time() - t0:.4f}s.")
    
if __name__ == '__main__':
    test_speed()
