from __future__ import annotations
from typing import Dict
from rich.console import Console
import questionary

from chess_manager.models.tournament_models import Tournament
from chess_manager.models.round_models import Round
from chess_manager.controllers.round_controller import score_round
from chess_manager.views.round_views import display_round_pairings
from chess_manager.views.tournament_views import (
    display_tournament_recap,
    display_tournament_description,
    prompt_description_menu,
    prompt_edit_description,
    confirm_clear_description
)

console = Console()


def launch_first_round_flow(tournament_dict: Dict) -> Tournament:
    """
    Construit un Tournament depuis un dict repo, lance le 1er round (pairings au niveau modèle),
    affiche les appariements, et retourne le modèle prêt à être scoré.
    """

    model = Tournament.from_dict(tournament_dict)
    if model.roster_size() < 8:
        raise ValueError("Il faut au moins 8 joueurs pour démarrer un tournoi.")

    confirm = questionary.confirm(
        f"Voulez-vous lancer le tournoi '{tournament_dict.get('name','(sans nom)')}' "
        f"avec {model.roster_size()} joueurs ?"
    ).ask()
    if not confirm:
        raise RuntimeError("Lancement annulé par l'utilisateur.")

    try:
        first_round: Round = model.start_first_round()
    except ValueError as e:
        raise ValueError(f"Impossible de lancer le 1er tour : {e}") from e
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la création du 1er tour : {e}") from e

    model.repo_name = tournament_dict.get("name", "") or model.repo_name
    display_round_pairings(first_round)
    return model


def run_rounds_until_done(model: Tournament, repo=None) -> None:
    """
    Score the current round, then keep creating/scoring next rounds until done.
    Before finishing, offer to edit description. Then finish, save, recap.
    """
    # Score the round that was just created/launched
    try:
        current = model.rounds[-1]
    except (IndexError, AttributeError):
        console.print("[red]Aucun round à scorer.[/red]")
        return

    try:
        done = score_round(model, current)
    except KeyboardInterrupt:
        console.print("[yellow]Saisie interrompue par l'utilisateur.[/yellow]")
        return
    except Exception as e:
        console.print(f"[red]Erreur pendant la saisie des résultats : {e}[/red]")
        return

    if not done:
        return

    # Next rounds
    while model.current_round_number < model.number_rounds:
        try:
            next_round = model.start_next_round()
        except ValueError as e:
            console.print(f"[red]Impossible de créer le tour suivant : {e}[/red]")
            break
        except Exception as e:
            console.print(f"[red]Erreur interne lors de la création d'un nouveau tour : {e}[/red]")
            break

        display_round_pairings(next_round)

        try:
            done = score_round(model, next_round)
        except KeyboardInterrupt:
            console.print("[yellow]Saisie interrompue par l'utilisateur.[/yellow]")
            return
        except Exception as e:
            console.print(f"[red]Erreur pendant la saisie des résultats : {e}[/red]")
            return

        if not done:
            return

        # Persist after each completed round (best effort, non-fatal on failure)
        if repo is not None:
            try:
                repo.save_tournament(model.to_dict())
            except Exception as e:
                console.print(f"[red]Échec de la sauvegarde après un tour : {e}[/red]")

    # Offer to edit description before finishing
    try:
        wants_desc = questionary.confirm(
            "Souhaitez-vous ajouter/modifier la description avant de clôturer le tournoi ?"
        ).ask()
    except KeyboardInterrupt:
        return
    except Exception:
        wants_desc = False

    if wants_desc:
        manage_tournament_description(model, repo=repo)

    # Finish + save + recap
    model.mark_finished()
    if repo is not None:
        try:
            repo.save_tournament(model.to_dict())
        except Exception as e:
            console.print(f"[red]Échec de la sauvegarde du tournoi finalisé : {e}[/red]")

    try:
        display_tournament_recap(model)
    except Exception as e:
        console.print(f"[red]Erreur lors de l'affichage du récapitulatif : {e}[/red]")


# ----------------------
# Modify and Clear Description flow
# ----------------------

def manage_tournament_description(model: Tournament, repo=None) -> None:
    """
    View/edit/clear the tournament single-string description.
    Saves after each modification when a repo is provided.
    """
    while True:
        display_tournament_description(model)
        action = prompt_description_menu()
        if action in (None, "back"):
            return

        if action == "edit":
            current = model.get_description() if hasattr(model, "get_description") else (model.description or "")
            try:
                new_text = prompt_edit_description(current)
            except KeyboardInterrupt:
                continue
            if new_text is not None:
                model.set_description(new_text)
            else:
                model.description = new_text
            if repo is not None:
                try:
                    repo.save_tournament(model.to_dict())
                except Exception as e:
                    console.print(f"[red]Échec de la sauvegarde de la description : {e}[/red]")

        elif action == "clear":
            try:
                if confirm_clear_description():
                    if hasattr(model, "set_description"):
                        model.set_description("")
                    else:
                        model.description = ""
                        if repo is not None:
                            try:
                                repo.save_tournament(model.to_dict())
                            except Exception as e:
                                console.print(f"[red]Échec de la sauvegarde de la description : {e}[/red]")
            except KeyboardInterrupt:
                continue

        else:
            console.print("[red]Option invalide.[/red]")
