from typing import Tuple

import jax
import jax.numpy as jnp

from qdax.types import Descriptor, ExtraScores, Fitness, Genotype, RNGKey

def arm(params: Genotype) -> Tuple[Fitness, Descriptor]:
    """
    Compute the fitness and BD of one individual in the Planar Arm task.
    Based on the Planar Arm implementation in fast_map_elites
    (https://github.com/hucebot/fast_map-elites).

    Args:
        params: genotype of the individual to evaluate, corresponding to
            the normalised angles for each DoF of the arm.

    Returns:
        f: the fitness of the individual, given as the variance of the angles.
        bd: the bd of the individual, given as the [x, y] position of the
            end-effector of the arm.
    """

    x = jnp.clip(params, 0, 1)
    size = params.shape[0]

    f = jnp.sqrt(jnp.mean(jnp.square(x - jnp.mean(x))))

    cum_angles = jnp.cumsum(2 * jnp.pi * x - jnp.pi)
    x_pos = jnp.sum(jnp.cos(cum_angles)) / (2 * size) + 0.5
    y_pos = jnp.sum(jnp.sin(cum_angles)) / (2 * size) + 0.5

    return -f, jnp.array([x_pos, y_pos])


def arm_scoring_function(
    params: Genotype,
    random_key: RNGKey,
    fit_variance: float,
    desc_variance: float,
) -> Tuple[Fitness, Descriptor, ExtraScores, RNGKey]:
    """
    Evaluate policies contained in params in parallel.
    """
    fitnesses, descriptors = jax.vmap(arm)(params)

    # Add noise
    random_key, subkey = jax.random.split(random_key)
    fitnesses = (
        fitnesses + jax.random.normal(subkey, shape=fitnesses.shape) * fit_variance
    )
    descriptors = (
        descriptors + jax.random.normal(subkey, shape=descriptors.shape) * desc_variance
    )

    return (
        fitnesses,
        descriptors,
        {},
        random_key,
    )




