from prefect import get_client
from prefect.exceptions import ObjectNotFound
from prefect.server.database.dependencies import provide_database_interface
from prefect.server.schemas.responses import SetStateStatus
from prefect.server.services.cancellation_cleanup import CancellationCleanup
from prefect.states import Cancelled

from core.lunarcore.utils import setup_logger

logger = setup_logger("callbacks")


async def cancelled_flow_handler(flow, flow_run, state) -> None:
    logger.info(
        f"Flow {flow.name} cancelled with message: {state.message}. Cleaning up ..."
    )
    async with get_client() as client:
        cancelling_state = Cancelled(
            message="Cancelled by admin!",
        )
        try:
            result = await client.set_flow_run_state(
                flow_run_id=flow_run.id, state=cancelling_state, force=True
            )
        except ObjectNotFound:
            logger.error(f"Flow run {flow_run.id} not found!")

        if result.status == SetStateStatus.ABORT:
            logger.error(
                f"Flow run {flow_run.id} was unable to be cancelled. Reason:"
                f" '{result.details.reason}'"
            )
            return

    await CancellationCleanup(handle_signals=True).run_once(
        db=provide_database_interface()
    )

    logger.info(f"Flow run {flow_run.id} " f"was successfully cancelled!")


def crashed_flow_handler(flow, flow_run, state) -> None:
    pass


def failed_flow_handler(flow, flow_run, state) -> None:
    pass


def completed_flow_handler(flow, flow_run, state) -> None:
    pass


def running_flow_handler(flow, flow_run, state) -> None:
    pass
